import os
from ftplib import FTP, error_perm

from web.logger import log
from web.setup import config

from .type import _SupportsRead


def filenames(path: str) -> list[str]:
    folder = os.path.dirname(path)
    with FTP(
        config.FTP_HOSTNAME,
        config.FTP_USERNAME,
        config.FTP_PASSWORD,
    ) as ftp:
        ftp.cwd(folder)
        return ftp.nlst()


def exists(path: str) -> bool:
    folder = os.path.dirname(path)
    name = os.path.basename(path)
    with FTP(
        config.FTP_HOSTNAME,
        config.FTP_USERNAME,
        config.FTP_PASSWORD,
    ) as ftp:
        ftp.cwd(folder)
        names = ftp.nlst()
        return name in names


def upload(file_: _SupportsRead[bytes], path: str) -> None:
    folder = os.path.dirname(path)
    name = os.path.basename(path)
    with FTP(
        config.FTP_HOSTNAME,
        config.FTP_USERNAME,
        config.FTP_PASSWORD,
    ) as ftp:
        try:
            ftp.mkd(folder)
        except error_perm as error:
            if error.args[0][:3] != "521":
                raise
        ftp.cwd(folder)
        ftp.storbinary(f"STOR {name}", file_)
    log.info(f"Uploaded on FTP: {path}")


def delete(path: str) -> None:
    with FTP(
        config.FTP_HOSTNAME,
        config.FTP_USERNAME,
        config.FTP_PASSWORD,
    ) as ftp:
        try:
            ftp.delete(path)
        except error_perm as error:
            if error.args[0][:3] != "550":
                raise
    log.info(f"Deleted on FTP: {path}")


def url(*args: str | None) -> str | None:
    parts = [x for x in args if x is not None]
    if not parts:
        return None
    return os.path.join(config.CDN_BASE_URL, *parts)
