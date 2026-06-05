import os
from contextlib import contextmanager
from datetime import datetime
from ftplib import FTP, error_perm
from typing import Iterator

from web.logger import log
from web.setup import config

from .type import _SupportsRead


def url(*args: str | None) -> str | None:
    parts = [x for x in args if x is not None]
    if not parts:
        return None
    return os.path.join(config.CDN_BASE_URL, *parts)


def _abs(rel: str) -> str:
    if config.FTP_BASE_DIR is not None:
        return os.path.join(config.FTP_BASE_DIR, rel)
    return rel


def _get_dir(rel_dir: str) -> str:
    return os.path.normpath(_abs(rel_dir))


def _get_file_dir(rel_fp: str) -> str:
    return os.path.dirname(_abs(rel_fp))


def _get_file_path(rel_fp: str) -> str:
    return _abs(rel_fp)


class Client:
    def __init__(self, ftp: FTP) -> None:
        self._ftp = ftp

    def filenames(self, path: str) -> list[str]:
        self._ftp.cwd(_get_dir(path))
        return self._ftp.nlst()

    def modified(self, path: str) -> dict[str, datetime]:
        self._ftp.cwd(_get_dir(path))
        times: dict[str, datetime] = {}
        for fn in self._ftp.nlst():
            try:
                resp = self._ftp.sendcmd(f"MDTM {fn}")
            except error_perm:
                continue
            if not resp.startswith("213"):
                continue
            stamp = resp[3:].strip()
            try:
                times[fn] = datetime.strptime(stamp[:14], "%Y%m%d%H%M%S")
            except ValueError:
                continue
        return times

    def exists(self, path: str) -> bool:
        self._ftp.cwd(_get_file_dir(path))
        return os.path.basename(path) in self._ftp.nlst()

    def upload(self, file_: _SupportsRead[bytes], path: str) -> None:
        dir_ = _get_file_dir(path)
        try:
            self._ftp.mkd(dir_)
        except error_perm as error:
            if error.args[0][:3] != "521":
                raise
        self._ftp.cwd(dir_)
        self._ftp.storbinary(f"STOR {os.path.basename(path)}", file_)
        log.info(f"Uploaded on FTP: {path}")

    def delete(self, path: str) -> None:
        try:
            self._ftp.delete(_get_file_path(path))
        except error_perm as error:
            if error.args[0][:3] != "550":
                raise
        log.info(f"Deleted on FTP: {path}")


#
# Deprecated
#


@contextmanager
def connect() -> Iterator[Client]:
    with FTP(
        config.FTP_HOSTNAME,
        config.FTP_USERNAME,
        config.FTP_PASSWORD,
    ) as ftp:
        yield Client(ftp)


def filenames(path: str) -> list[str]:
    with connect() as client:
        return client.filenames(path)


def modified(path: str) -> dict[str, datetime]:
    with connect() as client:
        return client.modified(path)


def exists(path: str) -> bool:
    with connect() as client:
        return client.exists(path)


def upload(file_: _SupportsRead[bytes], path: str) -> None:
    with connect() as client:
        client.upload(file_, path)


def delete(path: str) -> None:
    with connect() as client:
        client.delete(path)
