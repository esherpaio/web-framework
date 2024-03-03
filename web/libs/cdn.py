import os
from ftplib import FTP, error_perm

from _typeshed import SupportsRead

from web.config import config

#
# Functions
#


def upload(file_: SupportsRead[bytes], path: str) -> None:
    folder = os.path.dirname(path)
    name = os.path.basename(path)
    with FTP(
        config.CDN_HOSTNAME,
        config.CDN_USERNAME,
        config.CDN_PASSWORD,
    ) as ftp:
        try:
            ftp.mkd(folder)
        except error_perm as error:
            if error.args[0][:3] != "521":
                raise
        ftp.cwd(folder)
        ftp.storbinary(f"STOR {name}", file_)


def delete(path: str) -> None:
    with FTP(
        config.CDN_HOSTNAME,
        config.CDN_USERNAME,
        config.CDN_PASSWORD,
    ) as ftp:
        try:
            ftp.delete(path)
        except error_perm as error:
            if error.args[0][:3] != "550":
                raise


def url(*args: str) -> str:
    return os.path.join(config.CDN_URL, *args)
