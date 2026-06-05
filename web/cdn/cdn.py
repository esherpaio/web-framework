import os
from contextlib import contextmanager
from datetime import datetime
from ftplib import FTP, error_perm
from typing import Iterator, Protocol

from flask import current_app

from web.logger import log
from web.setup import config

from .type import _SupportsRead

if not config.DEBUG:
    STATIC_LOCAL = True
    STATIC_DIR = "static"
else:
    STATIC_LOCAL = False
    STATIC_DIR = "cdn"


def url(*args: str | None) -> str | None:
    parts = [x for x in args if x is not None]
    if not parts:
        return None
    rel = os.path.join(*parts)
    if config.DEBUG and rel.startswith(STATIC_DIR):
        if current_app.static_url_path is None:
            raise RuntimeError
        return os.path.join(current_app.static_url_path, rel)
    return os.path.join(config.CDN_BASE_URL, rel)


#
# Client
#


class BaseClient(Protocol):
    def filenames(self, path: str) -> list[str]: ...

    def modified(self, path: str) -> dict[str, datetime]: ...

    def exists(self, path: str) -> bool: ...

    def upload(self, file_: _SupportsRead[bytes], path: str) -> None: ...

    def delete(self, path: str) -> None: ...


class CdnClient(BaseClient):
    def __init__(self, ftp: FTP) -> None:
        self._ftp = ftp

    #
    # Private
    #

    @classmethod
    def _abs(cls, rel: str) -> str:
        if config.FTP_BASE_DIR is not None:
            return os.path.join(config.FTP_BASE_DIR, rel)
        return rel

    @classmethod
    def _get_dir(cls, rel_dir: str) -> str:
        return os.path.normpath(cls._abs(rel_dir))

    @classmethod
    def _get_file_dir(cls, rel_fp: str) -> str:
        return os.path.dirname(cls._abs(rel_fp))

    @classmethod
    def _get_file_path(cls, rel_fp: str) -> str:
        return cls._abs(rel_fp)

    #
    # Public
    #

    def filenames(self, path: str) -> list[str]:
        self._ftp.cwd(self._get_dir(path))
        return self._ftp.nlst()

    def modified(self, path: str) -> dict[str, datetime]:
        self._ftp.cwd(self._get_dir(path))
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
        self._ftp.cwd(self._get_file_dir(path))
        return os.path.basename(path) in self._ftp.nlst()

    def upload(self, file_: _SupportsRead[bytes], path: str) -> None:
        dir_ = self._get_file_dir(path)
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
            self._ftp.delete(self._get_file_path(path))
        except error_perm as error:
            if error.args[0][:3] != "550":
                raise
        log.info(f"Deleted on FTP: {path}")


class LocalClient(BaseClient):
    #
    # Private
    #

    @classmethod
    def _path(cls, rel: str) -> str:
        if current_app.static_folder is None:
            raise RuntimeError
        return os.path.join(current_app.static_folder, os.path.normpath(rel))

    #
    # Public
    #

    def filenames(self, path: str) -> list[str]:
        dir_ = self._path(path)
        if not os.path.isdir(dir_):
            return []
        return os.listdir(dir_)

    def modified(self, path: str) -> dict[str, datetime]:
        dir_ = self._path(path)
        times: dict[str, datetime] = {}
        if not os.path.isdir(dir_):
            return times
        for fn in os.listdir(dir_):
            fp = os.path.join(dir_, fn)
            if os.path.isfile(fp):
                times[fn] = datetime.fromtimestamp(os.path.getmtime(fp))
        return times

    def exists(self, path: str) -> bool:
        return os.path.isfile(self._path(path))

    def upload(self, file_: _SupportsRead[bytes], path: str) -> None:
        fp = self._path(path)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "wb") as out:
            out.write(file_.read())
        log.info(f"Saved locally: {path}")

    def delete(self, path: str) -> None:
        fp = self._path(path)
        if os.path.isfile(fp):
            os.remove(fp)
            log.info(f"Deleted locally: {path}")


#
# Deprecated
#


@contextmanager
def connect() -> Iterator[BaseClient]:
    if config.DEBUG:
        yield LocalClient()
        return
    with FTP(
        config.FTP_HOSTNAME,
        config.FTP_USERNAME,
        config.FTP_PASSWORD,
    ) as ftp:
        yield CdnClient(ftp)


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
