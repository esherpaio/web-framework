import hashlib
import os
from typing import Type

from web.helper.logger import logger
from web.packer.tag import CssPacker, JsPacker


class Packer:
    encoding = "utf-8"

    def pack(
        self,
        in_dir: str,
        packer: Type[CssPacker | JsPacker],
        out_dir: str | None,
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

        hash_ = hashlib.md5(compiled.encode(self.encoding)).hexdigest()
        logger.info(f"Compiled {packer.OUT_EXT} with hash {hash_}")

        if out_dir is not None:
            out_path = os.path.join(out_dir, f"{hash_}.{packer.OUT_EXT}")
            with open(out_path, "w", encoding=self.encoding) as file_:
                file_.write(compiled)

        if save_cdn:
            pass


if __name__ == "__main__":
    in_dir = "/Users/stan/code/web-framework/web/blueprint/admin/static/js"
    out_dir = "/Users/stan/code/web-framework"
    packer = Packer().pack(in_dir, JsPacker(), out_dir)
