import hashlib
import io
import os

from web.helper import cdn
from web.helper.logger import logger
from web.packer.bundle import CssBundle, JsBundle, ScssBundle


class Packer:
    encoding = "utf-8"

    def pack(
        self,
        packer: CssBundle | JsBundle | ScssBundle,
        out_dir: str | None = None,
        save_cdn: bool = True,
        *args,
        **kwargs,
    ) -> None:
        compiled = packer.compile(*args, **kwargs)
        bytes_ = compiled.encode(self.encoding)
        hash_ = hashlib.md5(bytes_).hexdigest()
        if compiled:
            if out_dir is not None:
                out_path = os.path.join(out_dir, f"{hash_}{packer.OUT_EXT}")
                with open(out_path, "w", encoding=self.encoding) as file_:
                    file_.write(compiled)
                logger.info(f"Saved bundle to {out_path}")
            if save_cdn:
                file_ = io.BytesIO(bytes_)  # type: ignore
                cdn_path = os.path.join("static", f"{hash_}{packer.OUT_EXT}")
                cdn.upload(file_, cdn_path)
                cdn_url = cdn.url(cdn_path)
                logger.info(f"Uploaded bundle to {cdn_url}")
