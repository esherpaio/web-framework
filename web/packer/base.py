import hashlib
import io
import os

import sass

from web.helper import cdn
from web.helper.logger import logger
from web.packer.tag import CssPacker, JsPacker, ScssPacker


class Packer:
    encoding = "utf-8"

    def pack(
        self,
        packer: CssPacker | JsPacker | ScssPacker,
        out_dir: str | None = None,
        save_cdn: bool = True,
        *args,
        **kwargs,
    ) -> None:
        compiled = packer.compile(*args, **kwargs)
        bytes_ = compiled.encode(self.encoding)
        hash_ = hashlib.md5(bytes_).hexdigest()
        logger.info(f"Compiled {packer.OUT_EXT} with hash {hash_}")

        if compiled:
            if out_dir is not None:
                out_path = os.path.join(out_dir, f"{hash_}{packer.OUT_EXT}")
                with open(out_path, "w", encoding=self.encoding) as file_:
                    file_.write(compiled)
                logger.info(f"Saved hash {hash_} to {out_path}")
            if save_cdn:
                file_ = io.BytesIO(bytes_)  # type: ignore
                cdn_path = os.path.join("static", f"{hash_}{packer.OUT_EXT}")
                cdn.upload(file_, cdn_path)
                logger.info(f"Uploaded hash {hash_} to {cdn_path}")


def compile_scss(src: str, out: str) -> None:
    scss = sass.compile(filename=src, output_style="compressed")
    with open(out, "w") as file_:
        file_.write(scss)
