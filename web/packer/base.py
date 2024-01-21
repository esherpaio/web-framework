import hashlib
import io
import os
from typing import Type

from web.helper import cdn
from web.helper.logger import logger
from web.packer.tag import CssPacker, JsPacker


class Packer:
    encoding = "utf-8"

    def pack(
        self,
        in_dir: str,
        packer: Type[CssPacker | JsPacker],
        out_dir: str | None = None,
        save_cdn: bool = True,
    ) -> None:
        if not os.path.isdir(in_dir):
            raise ValueError

        compiled = ""
        for subdir, _, fns in os.walk(in_dir):
            for fn in fns:
                if not any([fn.endswith(ext) for ext in packer.IN_EXTS]):
                    continue
                path = os.path.join(subdir, fn)
                content = open(path, "r", encoding=self.encoding).read()
                compiled += f"{packer.compile(content)}\n"

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
                file_ = io.BytesIO(bytes_)
                cdn_path = os.path.join("static", f"{hash_}{packer.OUT_EXT}")
                cdn.upload(file_, cdn_path)
                logger.info(f"Uploaded hash {hash_} to {cdn_path}")


if __name__ == "__main__":
    js_dir = "/Users/stan/code/web-framework/web/blueprint/admin/static/js"
    css_dir = "/Users/stan/code/web-framework/web/blueprint/admin/static/css"
    Packer().pack(js_dir, JsPacker(), save_cdn=True)
    Packer().pack(css_dir, CssPacker(), save_cdn=True)
