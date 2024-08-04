import sqlalchemy as sa
from alembic import op

revision = "423ebcd85503"
down_revision = "9915034938ed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add currency_code column
    op.add_column("order", sa.Column("currency_code", sa.String(length=3)))
    # Make curency_code not nullable
    op.alter_column(
        "order", "currency_code", existing_type=sa.String(length=3), nullable=False
    )
