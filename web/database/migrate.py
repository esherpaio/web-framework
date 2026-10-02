from alembic import context
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, make_url, text

from web.database.model import Base
from web.setup import config

from .client import engine


def get_revisions() -> tuple[str | None, str | None]:
    expected = ScriptDirectory.from_config(Config("alembic.ini")).get_current_head()
    with engine.connect() as conn:
        conn.execute(text("SET LOCAL statement_timeout = '10s'"))
        current = MigrationContext.configure(conn).get_current_revision()
    return current, expected


def create_database() -> None:
    db_url = make_url(config.DATABASE_URL)
    db_name = db_url.database
    pg_url = db_url.set(database="postgres")
    pg_engine = create_engine(
        pg_url,
        isolation_level="AUTOCOMMIT",
        connect_args={"connect_timeout": 10},
    )
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
