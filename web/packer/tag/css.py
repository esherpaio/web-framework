import re


class CssPacker:
    IN_EXTS = [".css"]
    OUT_EXT = ".css"

    @classmethod
    def compile(cls, css: str, *args: any, **kwargs: any) -> str:
        # remove comments
        css = re.sub(r"\s*/\*\s*\*/", "$$HACK1$$", css)  # preserve IE<6 comment hack
        css = re.sub(r"/\*[\s\S]*?\*/", "", css)
        css = css.replace("$$HACK1$$", "/**/")  # preserve IE<6 comment hack
        # spaces may be safely collapsed as generated content will collapse them anyway
        css = re.sub(r"\s+", " ", css)
        # shorten collapsable colors: #aabbcc to #abc
        css = re.sub(r"#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)", r"#\1\2\3\4", css)
        # fragment values can loose zeros
        css = re.sub(r":\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;", r":\1;", css)
        # strip css
        css = css.strip()
        return css
