from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from web.config import config


def init_db(*args, **kwargs):
    engine, conn = None, None
    if config.DATABASE_URL:
        engine = create_engine(config.DATABASE_URL, *args, **kwargs)
        conn = sessionmaker(engine, autoflush=False, expire_on_commit=False)
    return engine, conn


engine, conn = init_db()
