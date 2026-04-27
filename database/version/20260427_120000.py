import sqlalchemy as sa
from alembic import op

revision = "b1f4d2c8a901"
down_revision = "add0c6f4ccd6"
branch_labels = None
depends_on = None


def _fk_name(table: str, column: str):
    inspector = sa.inspect(op.get_bind())
    for fk in inspector.get_foreign_keys(table):
        if fk["constrained_columns"] == [column]:
            return fk["name"]
    raise RuntimeError(f"No FK found on {table}.{column}")


def upgrade() -> None:
    # 1. Add is_default columns (server_default false so existing rows backfill cleanly)
    op.add_column(
        "billing",
        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "shipping",
        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    # 2. Backfill: mark each user's currently-referenced billing/shipping as default.
    op.execute(
        "UPDATE billing SET is_default = true "
        'WHERE id IN (SELECT billing_id FROM "user" WHERE billing_id IS NOT NULL)'
    )
    op.execute(
        "UPDATE shipping SET is_default = true "
        'WHERE id IN (SELECT shipping_id FROM "user" WHERE shipping_id IS NOT NULL)'
    )

    # 3. Partial unique indexes: one default per user per table.
    op.create_index(
        None,
        "billing",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_default"),
    )
    op.create_index(
        None,
        "shipping",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_default"),
    )

    # 4. Drop user -> billing/shipping FKs and columns (breaks the circle).
    op.drop_constraint(_fk_name("user", "billing_id"), "user", type_="foreignkey")
    op.drop_constraint(_fk_name("user", "shipping_id"), "user", type_="foreignkey")
    op.drop_column("user", "billing_id")
    op.drop_column("user", "shipping_id")

    # 5. Recreate billing/shipping -> user FKs without use_alter (no longer circular).
    op.drop_constraint(_fk_name("billing", "user_id"), "billing", type_="foreignkey")
    op.drop_constraint(_fk_name("shipping", "user_id"), "shipping", type_="foreignkey")
    op.create_foreign_key(
        None,
        "billing",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None,
        "shipping",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
