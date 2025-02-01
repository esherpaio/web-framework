import hashlib
import io
import os

from web import cdn
from web.logger import log

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

    def write_file(
        self,
        data: str,
        hash_: str,
        out_dir: str,
        out_ext: str,
    ) -> str:
        out_path = os.path.join(out_dir, f"{hash_}{out_ext}")
        if not os.path.isfile(out_path):
            with open(out_path, "w", encoding=self.ENCODING) as file_:
                file_.write(data)
            log.info(f"Saved bundle to {out_path}")
        return out_path

    def write_cdn(
        self,
        data: bytes,
        cdn_path: str,
    ) -> str:
        if not cdn.exists(cdn_path):
            fileb = io.BytesIO(data)
            cdn.upload(fileb, cdn_path)
            cdn_url = cdn.url(cdn_path)
            log.info(f"Uploaded bundle to {cdn_url}")
        return cdn_path
