from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from web.setup import config


def init_db(uri: str | None = None, **options):
    if uri is None:
        uri = config.DATABASE_URL
    options.setdefault("pool_pre_ping", True)
    options.setdefault("pool_recycle", 300)
    options.setdefault("pool_size", 2)
    options.setdefault("max_overflow", 3)
    engine, conn = None, None
    if uri is not None:
        engine = create_engine(config.DATABASE_URL, **options)
        conn = sessionmaker(engine, autoflush=False, expire_on_commit=False)
    return engine, conn


engine, conn = init_db()
