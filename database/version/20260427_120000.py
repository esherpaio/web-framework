"""Break circular FK between user and billing/shipping.

- Add `is_default` boolean to billing and shipping (default false).
- Backfill `is_default=true` for the row currently referenced by user.billing_id /
  user.shipping_id, preserving each user's existing default.
- Add a partial unique index enforcing one default per user per table.
- Drop user.billing_id and user.shipping_id columns + their FKs.
- Recreate billing.user_id and shipping.user_id FKs without `use_alter` (no longer
  circular).
"""

import sqlalchemy as sa
from alembic import op

revision = "b1f4d2c8a901"
down_revision = "add0c6f4ccd6"
branch_labels = None
depends_on = None


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
        "ix_billing_user_default",
        "billing",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_default"),
    )
    op.create_index(
        "ix_shipping_user_default",
        "shipping",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_default"),
    )

    # 4. Drop user -> billing/shipping FKs and columns (breaks the circle).
    op.drop_constraint("user_billing_id_fkey", "user", type_="foreignkey")
    op.drop_constraint("user_shipping_id_fkey", "user", type_="foreignkey")
    op.drop_column("user", "billing_id")
    op.drop_column("user", "shipping_id")

    # 5. Recreate billing/shipping -> user FKs without use_alter (no longer circular).
    #    The original FKs were created with auto-generated names in 20250202_185952.
    #    Drop by inferred default name and recreate cleanly.
    op.drop_constraint("billing_user_id_fkey", "billing", type_="foreignkey")
    op.drop_constraint("shipping_user_id_fkey", "shipping", type_="foreignkey")
    op.create_foreign_key(
        "billing_user_id_fkey",
        "billing",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "shipping_user_id_fkey",
        "shipping",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # Recreate billing/shipping -> user FKs with use_alter.
    op.drop_constraint("billing_user_id_fkey", "billing", type_="foreignkey")
    op.drop_constraint("shipping_user_id_fkey", "shipping", type_="foreignkey")
    op.create_foreign_key(
        "billing_user_id_fkey",
        "billing",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
        use_alter=True,
    )
    op.create_foreign_key(
        "shipping_user_id_fkey",
        "shipping",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
        use_alter=True,
    )

    # Re-add user.billing_id / shipping_id columns + FKs.
    op.add_column(
        "user",
        sa.Column("billing_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "user",
        sa.Column("shipping_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "user_billing_id_fkey",
        "user",
        "billing",
        ["billing_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "user_shipping_id_fkey",
        "user",
        "shipping",
        ["shipping_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Backfill user.billing_id / shipping_id from is_default rows.
    op.execute(
        'UPDATE "user" SET billing_id = b.id '
        'FROM billing b WHERE b.user_id = "user".id AND b.is_default = true'
    )
    op.execute(
        'UPDATE "user" SET shipping_id = s.id '
        'FROM shipping s WHERE s.user_id = "user".id AND s.is_default = true'
    )

    # Drop is_default + indexes.
    op.drop_index("ix_billing_user_default", table_name="billing")
    op.drop_index("ix_shipping_user_default", table_name="shipping")
    op.drop_column("billing", "is_default")
    op.drop_column("shipping", "is_default")
