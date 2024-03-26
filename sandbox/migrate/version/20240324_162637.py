import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

from web.database.model import Order

revision = "423ebcd85503"
down_revision = "9915034938ed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get session
    bind = op.get_bind()
    s = orm.Session(bind=bind)
    # Add currency_code column
    op.add_column("order", sa.Column("currency_code", sa.String(length=3)))
    # Set currency_code on all orders
    for order in s.query(Order).join(Order.currency).all():  # type: ignore[attr-defined]
        order.currency_code = order.currency.code  # type: ignore[attr-defined]
    # Make curency_code not nullable
    op.alter_column(
        "order", "currency_code", existing_type=sa.String(length=3), nullable=False
    )
