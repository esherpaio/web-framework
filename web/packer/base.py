import hashlib
import io
import os

from web.libs import cdn
from web.libs.logger import log

from .bundle import CssBundle, JsBundle, ScssBundle


class Packer:
    ENCODING = "utf-8"

    def pack(
        self,
        bundle: CssBundle | JsBundle | ScssBundle,
        out_dir: str | None = None,
        save_cdn: bool = True,
        *args,
        **kwargs,
    ) -> tuple[str | None, str | None]:
        out_path, cdn_path = None, None
        compiled = bundle.compile(*args, **kwargs)
        bytes_ = compiled.encode(self.ENCODING)
        hash_ = hashlib.md5(bytes_).hexdigest()
        if compiled:
            if out_dir is not None:
                out_path = os.path.join(out_dir, f"{hash_}{bundle.OUT_EXT}")
                with open(out_path, "w", encoding=self.ENCODING) as file_:
                    file_.write(compiled)
                log.info(f"Saved bundle to {out_path}")
            if save_cdn:
                fileb = io.BytesIO(bytes_)
                cdn_path = os.path.join("static", f"{hash_}{bundle.OUT_EXT}")
                cdn.upload(fileb, cdn_path)
                cdn_url = cdn.url(cdn_path)
                log.info(f"Uploaded bundle to {cdn_url}")
        return out_path, cdn_path
