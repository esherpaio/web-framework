import os
from ftplib import FTP, error_perm

from web.logger import log
from web.setup import config

from .type import _SupportsRead


def _get_dir(rel_dir: str) -> str:
    if config.FTP_BASE_DIR is not None:
        dir_ = os.path.dirname(os.path.join(config.FTP_BASE_DIR, rel_dir))
    else:
        dir_ = os.path.dirname(rel_dir)
    return dir_


def _get_path(rel_fp: str) -> str:
    if config.FTP_BASE_DIR is not None:
        fp = os.path.join(config.FTP_BASE_DIR, rel_fp)
    else:
        fp = rel_fp
    return fp


def filenames(path: str) -> list[str]:
    dir_ = _get_dir(path)
    with FTP(
        config.FTP_HOSTNAME,
        config.FTP_USERNAME,
        config.FTP_PASSWORD,
    ) as ftp:
        ftp.cwd(dir_)
        fns = ftp.nlst()
    return fns


def exists(path: str) -> bool:
    dir_ = _get_dir(path)
    fn = os.path.basename(path)
    with FTP(
        config.FTP_HOSTNAME,
        config.FTP_USERNAME,
        config.FTP_PASSWORD,
    ) as ftp:
        ftp.cwd(dir_)
        fns = ftp.nlst()
    return fn in fns


def upload(file_: _SupportsRead[bytes], path: str) -> None:
    dir_ = _get_dir(path)
    fn = os.path.basename(path)
    with FTP(
        config.FTP_HOSTNAME,
        config.FTP_USERNAME,
        config.FTP_PASSWORD,
    ) as ftp:
        try:
            ftp.mkd(dir_)
        except error_perm as error:
            if error.args[0][:3] != "521":
                raise
        ftp.cwd(dir_)
        ftp.storbinary(f"STOR {fn}", file_)
    log.info(f"Uploaded on FTP: {path}")


def delete(path: str) -> None:
    fp = _get_path(path)
    with FTP(
        config.FTP_HOSTNAME,
        config.FTP_USERNAME,
        config.FTP_PASSWORD,
    ) as ftp:
        try:
            ftp.delete(fp)
        except error_perm as error:
            if error.args[0][:3] != "550":
                raise
    log.info(f"Deleted on FTP: {path}")


def url(*args: str | None) -> str | None:
    parts = [x for x in args if x is not None]
    if not parts:
        return None
    return os.path.join(config.CDN_BASE_URL, *parts)
