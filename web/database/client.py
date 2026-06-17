from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from web.logger import log
from web.setup import config


def init_db(uri: str | None = None, **options):
    if uri is None:
        uri = config.DATABASE_URL
    if uri is None:
        log.error("Database URL unset")
        raise EnvironmentError

    engine = create_engine(
        uri,
        pool_pre_ping=True,  # Check if connection is alive before using
        pool_size=2,  # Keep x connections open in pool
        max_overflow=5,  # Allow x extra connections when pool is full
        pool_recycle=300,  # Recycle connections after x seconds
        pool_timeout=30,  # Wait up to x seconds for a connection
    )
    conn = sessionmaker(engine, autoflush=False, expire_on_commit=False)
    return engine, conn


engine, conn = init_db()
