from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from webshop import config

_Engine = create_engine(config.DATABASE_URL, echo=False)
Conn = sessionmaker(_Engine, autoflush=False, expire_on_commit=False)
