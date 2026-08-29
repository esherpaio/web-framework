from pathlib import Path

import pytest

from web.packer import (
    CssPurgeConfig,
    CssPurgeError,
    CssPurger,
    CssPurgeResult,
    CssSafelist,
)
from web.packer.bundle import ScssBundle


def purge_css(
    tmp_path: Path,
    css: str,
    content: str,
    *,
    safelist: CssSafelist | None = None,
    preserve_dynamic_prefixes: bool = True,
) -> CssPurgeResult:
    template = tmp_path / "template.html"
    template.write_text(content, encoding="utf-8")
    config = CssPurgeConfig(
        content_paths=[template],
        safelist=safelist or CssSafelist(),
        preserve_dynamic_prefixes=preserve_dynamic_prefixes,
    )
    return CssPurger(config).purge(css)


def test_removes_unused_selectors_and_comma_branches(tmp_path: Path) -> None:
    result = purge_css(
        tmp_path,
        ".used,.unused{color:red}@media(min-width:1px){#present{display:block}"
        ".absent{display:none}}",
        '<div id="present" class="used"></div>',
    )

    assert ".used" in result.css
    assert ".unused" not in result.css
    assert "#present" in result.css
    assert ".absent" not in result.css
    assert result.selectors_total == 4
    assert result.selectors_removed == 2
    assert result.source_files_scanned == 1
    assert {item.selector for item in result.removed_selectors} == {
        ".unused",
        ".absent",
    }


def test_preserves_selectors_without_class_or_id_requirements(tmp_path: Path) -> None:
    css = (
        "body{margin:0}[aria-hidden=true]{display:none}"
        "@font-face{font-family:test;src:url(test.woff2)}"
        "@keyframes spin{from{opacity:0}to{opacity:1}}"
    )

    result = purge_css(tmp_path, css, "<body></body>")

    assert "body" in result.css
    assert "[aria-hidden=true]" in result.css
    assert "@font-face" in result.css
    assert "@keyframes spin" in result.css


def test_supports_tailwind_style_escaped_utility_names(tmp_path: Path) -> None:
    css = (
        r".md\:flex{display:flex}.w-1\/2{width:50%}"
        r".unused\:thing{visibility:hidden}"
    )

    result = purge_css(
        tmp_path,
        css,
        '<div class="md:flex w-1/2"></div>',
    )

    assert "display:flex" in result.css
    assert "width:50%" in result.css
    assert "visibility:hidden" not in result.css


def test_scans_javascript_for_runtime_classes(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    javascript = source_dir / "modal.js"
    javascript.write_text(
        'document.body.classList.add("modal-backdrop")',
        encoding="utf-8",
    )
    config = CssPurgeConfig(content_paths=[source_dir])

    result = CssPurger(config).purge(
        ".modal-backdrop{position:fixed}.unused{display:none}"
    )

    assert ".modal-backdrop" in result.css
    assert ".unused" not in result.css


def test_excludes_dependency_and_generated_directories(tmp_path: Path) -> None:
    template = tmp_path / "template.html"
    template.write_text('<div class="used"></div>', encoding="utf-8")
    dependencies = tmp_path / "node_modules"
    dependencies.mkdir()
    dependency = dependencies / "dependency.js"
    dependency.write_text('classList.add("dependency-only")', encoding="utf-8")
    css = ".used{display:block}.dependency-only{display:none}"

    excluded = CssPurger(CssPurgeConfig(content_paths=[tmp_path])).purge(css)
    included = CssPurger(
        CssPurgeConfig(content_paths=[tmp_path], excluded_directories=set())
    ).purge(css)

    assert ".dependency-only" not in excluded.css
    assert excluded.source_files_scanned == 1
    assert ".dependency-only" in included.css
    assert included.source_files_scanned == 2


def test_safelist_supports_exact_names_and_patterns(tmp_path: Path) -> None:
    result = purge_css(
        tmp_path,
        ".exact{color:red}.prefix-one{color:blue}.remove{color:black}",
        "<div></div>",
        safelist=CssSafelist(
            names={"exact"},
            patterns=[r"^prefix-"],
        ),
    )

    assert ".exact" in result.css
    assert ".prefix-one" in result.css
    assert ".remove" not in result.css


def test_dynamic_prefixes_can_be_preserved_or_disabled(tmp_path: Path) -> None:
    css = ".btn-danger{color:red}.unused{color:blue}"
    content = '<button class="btn-{{ theme }} {{ extra_class }}"></button>'

    preserved = purge_css(tmp_path, css, content)
    strict = purge_css(
        tmp_path,
        css,
        content,
        preserve_dynamic_prefixes=False,
    )

    assert ".btn-danger" in preserved.css
    assert ".unused" not in preserved.css
    assert preserved.dynamic_prefixes == ["btn-"]
    assert len(preserved.dynamic_references) == 1
    assert preserved.dynamic_references[0].expression == "extra_class"
    assert ".btn-danger" not in strict.css


def test_complex_selectors_are_retained_unless_an_outer_name_is_missing(
    tmp_path: Path,
) -> None:
    result = purge_css(
        tmp_path,
        ":is(.unknown,.other){color:red}.missing:not(.state){color:blue}",
        "<div></div>",
    )

    assert ":is(.unknown,.other)" in result.css
    assert ".missing" not in result.css
    assert result.selectors_retained_as_complex == 1


def test_rejects_missing_or_empty_content_paths(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        CssPurgeConfig(content_paths=[])

    config = CssPurgeConfig(content_paths=[tmp_path / "missing"])
    with pytest.raises(CssPurgeError, match="does not exist"):
        CssPurger(config).purge(".unused{color:red}")


def test_scss_bundle_can_purge_compiled_output(tmp_path: Path) -> None:
    scss = tmp_path / "main.scss"
    scss.write_text(
        ".used { color: red; } .unused { color: blue; }",
        encoding="utf-8",
    )
    template = tmp_path / "template.html"
    template.write_text('<div class="used"></div>', encoding="utf-8")

    normal_css = ScssBundle(str(scss)).compile()
    purged_css = ScssBundle(
        str(scss),
        purge=CssPurgeConfig(content_paths=[template]),
    ).compile()

    assert ".used" in normal_css
    assert ".unused" in normal_css
    assert ".used" in purged_css
    assert ".unused" not in purged_css
