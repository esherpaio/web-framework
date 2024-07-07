import time
from random import randint

from flask import g

from .enum import AuthType


def jwt_login(user_id: int) -> None:
    time.sleep(randint(0, 1000) / 1000)
    g._user = None
    g._user_id = user_id
    g._auth_type = AuthType.JWT


def jwt_logout() -> None:
    time.sleep(randint(0, 1000) / 1000)
    g._user = None
    g._user_id = None
    g._auth_type = AuthType.NONE
