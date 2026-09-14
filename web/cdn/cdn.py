import os
import posixpath
from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from ftplib import FTP, error_perm

from web.logger import log
from web.setup import config

from .type import _SupportsRead

CDN_DIR = "static"
LOCAL_DIR = os.path.join("static", "cdn")
LOCAL_URL = "/static/cdn"


def cdn_url(*args: str | None, external: bool = False) -> str | None:
    path_parts = [x for x in args if x is not None]
    if not path_parts:
        return None
    path = posixpath.join(*path_parts)
    if path.startswith(("http://", "https://")):
        return path
    if not external and config.CDN_LOCAL and os.path.isfile(LocalClient._path(path)):
        return posixpath.join(LOCAL_URL, path.lstrip("/"))
    return posixpath.join(config.CDN_BASE_URL, path.lstrip("/"))


#
# Client
#


class Client(ABC):
    @classmethod
    @contextmanager
    def connect(cls) -> Generator["Client", None, None]:
        if config.CDN_LOCAL:
            yield LocalClient()
        else:
            with FTP(
                config.FTP_HOSTNAME,
                config.FTP_USERNAME,
                config.FTP_PASSWORD,
            ) as ftp:
                yield CdnClient(ftp)

    @abstractmethod
    def filenames(self, path: str) -> list[str]: ...

    @abstractmethod
    def modified(self, path: str) -> dict[str, datetime]: ...

    @abstractmethod
    def exists(self, path: str) -> bool: ...

    @abstractmethod
    def upload(self, file_: _SupportsRead[bytes], path: str) -> None: ...

    @abstractmethod
    def delete(self, path: str) -> None: ...


class CdnClient(Client):
    def __init__(self, ftp: FTP) -> None:
        self._ftp = ftp
        self._home = ftp.pwd()

    def _path(self, rel: str) -> str:
        parts = [self._home]
        if config.FTP_BASE_DIR is not None:
            parts.append(config.FTP_BASE_DIR)
        parts.append(rel)
        return os.path.normpath(os.path.join(*parts))

    def filenames(self, path: str) -> list[str]:
        self._ftp.cwd(self._path(path))
        return self._ftp.nlst()

    def modified(self, path: str) -> dict[str, datetime]:
        self._ftp.cwd(self._path(path))
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
        self._ftp.cwd(os.path.dirname(self._path(path)))
        return os.path.basename(path) in self._ftp.nlst()

    def upload(self, file_: _SupportsRead[bytes], path: str) -> None:
        dir_ = os.path.dirname(self._path(path))
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
            self._ftp.delete(self._path(path))
        except error_perm as error:
            if error.args[0][:3] != "550":
                raise
        log.info(f"Deleted on FTP: {path}")


class LocalClient(Client):
    @classmethod
    def _path(cls, rel: str) -> str:
        root = os.path.join(config.BASE_DIR, LOCAL_DIR)
        path = os.path.normpath(os.path.join(root, rel.lstrip("/")))
        if path != root and not path.startswith(f"{root}{os.sep}"):
            raise ValueError(f"Invalid CDN path: {rel}")
        return path

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
