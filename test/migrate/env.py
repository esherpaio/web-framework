from alembic import context

from web.config import config
from web.database.client import engine
from web.database.model import Base


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    context.config.set_main_option("sqlalchemy.url", config.DATABASE_URL)
    context.configure(
        url=config.DATABASE_URL,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    with engine.connect() as conn:
        context.configure(
            connection=conn,
            target_metadata=Base.metadata,
            include_schemas=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
