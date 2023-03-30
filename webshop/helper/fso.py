import glob
import os
import time
from threading import Thread


def remove_dir(path: str) -> None:
    if os.path.isdir(path):
        path = f"{path.rstrip('/')}/*"
        for file in glob.glob(path):
            if os.access(file, os.W_OK):
                os.remove(file)


def remove_file(path: str, delay_s: int = 0) -> None:
    def remove() -> None:
        if delay_s:
            time.sleep(delay_s)
        if os.path.isfile(path):
            os.remove(path)

    Thread(target=remove, daemon=True).start()
