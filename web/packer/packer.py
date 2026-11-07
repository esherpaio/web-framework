import hashlib

from .bundle import CssBundle, JsBundle, ScssBundle


class Packer:
    ENCODING = "utf-8"

    def validate(
        self,
        bundles: list[CssBundle | JsBundle | ScssBundle],
    ) -> str:
        if not bundles:
            raise ValueError("No bundles to pack")
        out_ext = bundles[0].OUT_EXT
        if not all(x.OUT_EXT == out_ext for x in bundles):
            raise ValueError("All bundles must have the same output extension")
        return out_ext

    def pack(
        self,
        bundles: list[CssBundle | JsBundle | ScssBundle],
        *args,
        **kwargs,
    ) -> tuple[str, bytes, str]:
        compiled = "".join(x.compile(*args, **kwargs) for x in bundles)
        bytes_ = compiled.encode(self.ENCODING)
        hash_ = hashlib.md5(bytes_).hexdigest()
        return compiled, bytes_, hash_
