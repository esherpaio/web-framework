import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

import tinycss2
from tinycss2.ast import (
    AtRule,
    Comment,
    CurlyBracketsBlock,
    FunctionBlock,
    HashToken,
    IdentToken,
    LiteralToken,
    Node,
    ParenthesesBlock,
    ParseError,
    QualifiedRule,
    WhitespaceToken,
)

SIMPLE_NAME_RE = re.compile(r"[-_A-Za-z][-_A-Za-z0-9]*")
DYNAMIC_PREFIX_RE = re.compile(r"(?P<prefix>[-_A-Za-z][-_A-Za-z0-9]*-)\s*(?:\{\{|\$\{)")
CLASS_ATTRIBUTE_RE = re.compile(
    r"\bclass(?:Name)?\s*=\s*(?P<quote>[\"'])(?P<value>.*?)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)
JINJA_EXPRESSION_RE = re.compile(r"\{\{(?P<expression>.*?)\}\}", re.DOTALL)

DEFAULT_CONTENT_EXTENSIONS = {
    ".html",
    ".jinja",
    ".jinja2",
    ".js",
    ".jsx",
    ".py",
    ".ts",
    ".tsx",
}
DEFAULT_EXCLUDED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "venv",
}
NESTED_RULE_AT_KEYWORDS = {
    "-moz-document",
    "-webkit-keyframes",
    "container",
    "document",
    "keyframes",
    "layer",
    "media",
    "scope",
    "starting-style",
    "supports",
}


class CssPurgeError(Exception):
    """Raised when CSS purging cannot complete safely."""


@dataclass
class CssSafelist:
    """Class and ID names that static source scanning cannot discover."""

    names: set[str] = field(default_factory=set)
    patterns: list[str] = field(default_factory=list)


@dataclass
class CssPurgeConfig:
    """Configuration for matching compiled selectors against source content."""

    content_paths: list[str | Path]
    content_extensions: set[str] = field(
        default_factory=lambda: set(DEFAULT_CONTENT_EXTENSIONS)
    )
    excluded_directories: set[str] = field(
        default_factory=lambda: set(DEFAULT_EXCLUDED_DIRECTORIES)
    )
    safelist: CssSafelist = field(default_factory=CssSafelist)
    preserve_dynamic_prefixes: bool = True

    def __post_init__(self) -> None:
        if not self.content_paths:
            raise ValueError("CSS purge content paths cannot be empty")

        extensions = {
            extension.lower() if extension.startswith(".") else f".{extension.lower()}"
            for extension in self.content_extensions
            if extension
        }
        if not extensions:
            raise ValueError("CSS purge content extensions cannot be empty")

        self.content_extensions = extensions


@dataclass
class CssDynamicReference:
    """A template expression that can supply an unrestricted class value."""

    path: Path
    line: int
    expression: str


@dataclass
class CssRemovedSelector:
    """A removed selector and the required names missing from source content."""

    selector: str
    missing_names: list[str]


@dataclass
class CssPurgeResult:
    """Compiled CSS and typed diagnostics from one purge operation."""

    css: str
    source_files_scanned: int
    selectors_total: int
    selectors_removed: int
    selectors_retained_as_complex: int
    bytes_before: int
    bytes_after: int
    dynamic_prefixes: list[str]
    dynamic_references: list[CssDynamicReference]
    removed_selectors: list[CssRemovedSelector]


@dataclass
class _SourceIndex:
    files: list[Path]
    used_names: set[str]
    dynamic_prefixes: set[str]
    dynamic_references: list[CssDynamicReference]


@dataclass
class _SelectorAnalysis:
    required_names: set[str]
    is_complex: bool


@dataclass
class _PurgeStats:
    selectors_total: int = 0
    selectors_removed: int = 0
    selectors_retained_as_complex: int = 0
    removed_selectors: list[CssRemovedSelector] = field(default_factory=list)


class CssPurger:
    """Remove selectors that cannot match names found in configured sources."""

    def __init__(self, config: CssPurgeConfig) -> None:
        self._config = config
        self._safelist_patterns = [
            re.compile(pattern) for pattern in config.safelist.patterns
        ]

    def purge(self, css: str) -> CssPurgeResult:
        rules = tinycss2.parse_stylesheet(
            css,
            skip_comments=False,
            skip_whitespace=False,
        )
        self._raise_parse_errors(rules, "stylesheet")

        candidate_names = self._collect_candidate_names(rules, "stylesheet")
        source_index = self._build_source_index(candidate_names)
        stats = _PurgeStats()
        purged_rules = self._purge_rule_list(
            rules,
            source_index,
            stats,
            "stylesheet",
        )
        purged_css = tinycss2.serialize(purged_rules)

        return CssPurgeResult(
            css=purged_css,
            source_files_scanned=len(source_index.files),
            selectors_total=stats.selectors_total,
            selectors_removed=stats.selectors_removed,
            selectors_retained_as_complex=stats.selectors_retained_as_complex,
            bytes_before=len(css.encode("utf-8")),
            bytes_after=len(purged_css.encode("utf-8")),
            dynamic_prefixes=sorted(source_index.dynamic_prefixes),
            dynamic_references=source_index.dynamic_references,
            removed_selectors=stats.removed_selectors,
        )

    def _build_source_index(self, candidate_names: set[str]) -> _SourceIndex:
        files = list(self._iter_source_files())
        if not files:
            raise CssPurgeError(
                "No CSS purge source files matched the configured content paths"
            )

        simple_tokens: set[str] = set()
        source_parts: list[str] = []
        dynamic_prefixes: set[str] = set()
        dynamic_references: list[CssDynamicReference] = []

        for path in files:
            text = path.read_text(encoding="utf-8", errors="replace")
            source_parts.append(text)
            simple_tokens.update(SIMPLE_NAME_RE.findall(text))
            dynamic_prefixes.update(
                match.group("prefix") for match in DYNAMIC_PREFIX_RE.finditer(text)
            )
            if path.suffix.lower() in {".html", ".jinja", ".jinja2"}:
                dynamic_references.extend(self._find_dynamic_references(path, text))

        all_source = "\n".join(source_parts)
        used_names = {
            name
            for name in candidate_names
            if (
                name in simple_tokens
                if SIMPLE_NAME_RE.fullmatch(name)
                else name in all_source
            )
        }

        return _SourceIndex(
            files=files,
            used_names=used_names,
            dynamic_prefixes=dynamic_prefixes,
            dynamic_references=dynamic_references,
        )

    def _iter_source_files(self) -> Iterable[Path]:
        files: set[Path] = set()
        for configured_path in self._config.content_paths:
            path = Path(configured_path)
            if path.is_file():
                if path.suffix.lower() in self._config.content_extensions:
                    files.add(path.resolve())
                continue
            if not path.is_dir():
                raise CssPurgeError(f"CSS purge content path does not exist: {path}")

            for root, directories, names in os.walk(path):
                directories[:] = [
                    directory
                    for directory in directories
                    if directory not in self._config.excluded_directories
                ]
                root_path = Path(root)
                for name in names:
                    candidate = root_path / name
                    if candidate.suffix.lower() in self._config.content_extensions:
                        files.add(candidate.resolve())

        yield from sorted(files)

    @staticmethod
    def _find_dynamic_references(
        path: Path,
        text: str,
    ) -> list[CssDynamicReference]:
        references = []
        for attribute_match in CLASS_ATTRIBUTE_RE.finditer(text):
            value = attribute_match.group("value")
            value_offset = attribute_match.start("value")
            for expression_match in JINJA_EXPRESSION_RE.finditer(value):
                expression = expression_match.group("expression").strip()
                if '"' in expression or "'" in expression:
                    continue

                prefix_text = value[: expression_match.start()]
                if re.search(r"[-_A-Za-z][-_A-Za-z0-9]*-$", prefix_text):
                    continue

                absolute_offset = value_offset + expression_match.start()
                references.append(
                    CssDynamicReference(
                        path=path,
                        line=text.count("\n", 0, absolute_offset) + 1,
                        expression=expression,
                    )
                )
        return references

    def _collect_candidate_names(
        self,
        rules: Sequence[Node],
        context: str,
    ) -> set[str]:
        self._raise_parse_errors(rules, context)
        names: set[str] = set()

        for rule in rules:
            if isinstance(rule, QualifiedRule):
                for selector_tokens in self._split_selector_list(rule.prelude):
                    names.update(self._analyse_selector(selector_tokens).required_names)
                continue

            if (
                isinstance(rule, AtRule)
                and rule.content is not None
                and rule.lower_at_keyword in NESTED_RULE_AT_KEYWORDS
            ):
                nested_context = f"{context} @{rule.lower_at_keyword}"
                nested_rules = tinycss2.parse_rule_list(
                    rule.content,
                    skip_comments=False,
                    skip_whitespace=False,
                )
                names.update(
                    self._collect_candidate_names(nested_rules, nested_context)
                )

        return names

    def _purge_rule_list(
        self,
        rules: Sequence[Node],
        source_index: _SourceIndex,
        stats: _PurgeStats,
        context: str,
    ) -> list[Node]:
        self._raise_parse_errors(rules, context)
        output = []

        for rule in rules:
            if isinstance(rule, QualifiedRule):
                selector_lists = self._split_selector_list(rule.prelude)
                kept_selectors = []

                for selector_tokens in selector_lists:
                    selector = tinycss2.serialize(selector_tokens).strip()
                    if not selector:
                        continue

                    stats.selectors_total += 1
                    analysis = self._analyse_selector(selector_tokens)
                    missing_names = sorted(
                        name
                        for name in analysis.required_names
                        if not self._is_name_present(name, source_index)
                    )
                    if missing_names:
                        stats.selectors_removed += 1
                        stats.removed_selectors.append(
                            CssRemovedSelector(selector, missing_names)
                        )
                        continue

                    if analysis.is_complex:
                        stats.selectors_retained_as_complex += 1
                    kept_selectors.append(selector)

                if kept_selectors:
                    if len(kept_selectors) != len(selector_lists):
                        rule.prelude = tinycss2.parse_component_value_list(
                            ",".join(kept_selectors)
                        )
                    output.append(rule)
                continue

            if (
                isinstance(rule, AtRule)
                and rule.content is not None
                and rule.lower_at_keyword in NESTED_RULE_AT_KEYWORDS
            ):
                nested_context = f"{context} @{rule.lower_at_keyword}"
                nested_rules = tinycss2.parse_rule_list(
                    rule.content,
                    skip_comments=False,
                    skip_whitespace=False,
                )
                nested_output = self._purge_rule_list(
                    nested_rules,
                    source_index,
                    stats,
                    nested_context,
                )
                has_content = any(
                    not isinstance(node, (Comment, WhitespaceToken))
                    for node in nested_output
                )
                if has_content:
                    rule.content = tinycss2.parse_component_value_list(
                        tinycss2.serialize(nested_output)
                    )
                    output.append(rule)
                continue

            output.append(rule)

        return output

    def _is_name_present(self, name: str, source_index: _SourceIndex) -> bool:
        if name in source_index.used_names or name in self._config.safelist.names:
            return True
        if any(pattern.search(name) for pattern in self._safelist_patterns):
            return True
        return self._config.preserve_dynamic_prefixes and any(
            name.startswith(prefix) for prefix in source_index.dynamic_prefixes
        )

    @staticmethod
    def _split_selector_list(prelude: Sequence[Node]) -> list[list[Node]]:
        selectors: list[list[Node]] = [[]]
        for token in prelude:
            if isinstance(token, LiteralToken) and token.value == ",":
                selectors.append([])
            else:
                selectors[-1].append(token)
        return selectors

    @staticmethod
    def _analyse_selector(tokens: Sequence[Node]) -> _SelectorAnalysis:
        required_names: set[str] = set()
        is_complex = False

        for index, token in enumerate(tokens):
            if isinstance(token, LiteralToken) and token.value == ".":
                if index + 1 < len(tokens):
                    next_token = tokens[index + 1]
                    if isinstance(next_token, IdentToken):
                        required_names.add(next_token.value)
                continue
            if isinstance(token, HashToken) and token.is_identifier:
                required_names.add(token.value)
                continue
            if isinstance(
                token,
                (FunctionBlock, ParenthesesBlock, CurlyBracketsBlock),
            ):
                is_complex = True

        return _SelectorAnalysis(required_names, is_complex)

    @staticmethod
    def _raise_parse_errors(nodes: Sequence[Node], context: str) -> None:
        for node in nodes:
            if not isinstance(node, ParseError):
                continue
            raise CssPurgeError(
                f"{context}:{node.source_line}:{node.source_column}: {node.message}"
            )
