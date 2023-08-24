import glob
import os
import time
from threading import Thread

#
# Functions
#


def remove_dir(path: str) -> None:
    """Remove the content of a directory."""
    if os.path.isdir(path):
        for file in glob.glob(f"{path.rstrip('/')}/*"):
            if os.access(file, os.W_OK):
                os.remove(file)


def remove_file(path: str, delay_s: int = 0) -> None:
    """Remove a file with an optional delay."""

    def remove() -> None:
        if delay_s:
            time.sleep(delay_s)
        if os.path.isfile(path):
            os.remove(path)

    Thread(target=remove, daemon=True).start()
