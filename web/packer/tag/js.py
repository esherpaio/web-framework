from rjsmin import jsmin


class JsPacker(object):
    IN_EXTS = [".js"]
    OUT_EXT = ".js"

    @classmethod
    def compile(cls, js: str, *args, **kwargs) -> str:
        return jsmin(js)
