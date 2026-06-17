from alembic import context
from sqlalchemy import create_engine, make_url, text

from web.database.model import Base
from web.setup import config

from .client import engine


def create_database() -> None:
    db_url = make_url(config.DATABASE_URL)
    db_name = db_url.database
    pg_url = db_url.set(database="postgres")
    pg_engine = create_engine(pg_url, isolation_level="AUTOCOMMIT")
    with pg_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
        if exists:
            return
        conn.execute(text(f'CREATE DATABASE "{db_name}"'))


def run_migrations() -> None:
    create_database()
    with engine.connect() as conn:
        context.configure(
            connection=conn,
            target_metadata=Base.metadata,
            include_schemas=True,
            compare_type=True,
            compare_server_default=True,
            transaction_per_migration=True,
        )
        with context.begin_transaction():
            context.run_migrations()
