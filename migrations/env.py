from alembic import context

from web.database import engine
from web.database.model import Base


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    with engine.connect() as conn:
        context.configure(
            connection=conn,
            target_metadata=Base.metadata,
            include_schemas=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
