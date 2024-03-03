import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "d8912816ad82"
down_revision = "6f9921471217"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "app_blueprint",
        "attributes",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
        existing_server_default=sa.text("'{}'::json"),  # type: ignore[arg-type]
        server_default=sa.text("'{}'::jsonb"),
    )
    op.alter_column(
        "app_route",
        "attributes",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
        existing_server_default=sa.text("'{}'::json"),  # type: ignore[arg-type]
        server_default=sa.text("'{}'::jsonb"),
    )
    op.alter_column(
        "article",
        "attributes",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
        existing_server_default=sa.text("'{}'::json"),  # type: ignore[arg-type]
        server_default=sa.text("'{}'::jsonb"),
    )

    op.alter_column(
        "category",
        "attributes",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
        existing_server_default=sa.text("'{}'::json"),  # type: ignore[arg-type]
        server_default=sa.text("'{}'::jsonb"),
    )
    op.alter_column(
        "invoice",
        "attributes",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
        existing_server_default=sa.text("'{}'::json"),  # type: ignore[arg-type]
        server_default=sa.text("'{}'::jsonb"),
    )
    op.alter_column(
        "product",
        "attributes",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
        existing_server_default=sa.text("'{}'::json"),  # type: ignore[arg-type]
        server_default=sa.text("'{}'::jsonb"),
    )
    op.alter_column(
        "refund",
        "attributes",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
        existing_server_default=sa.text("'{}'::json"),  # type: ignore[arg-type]
        server_default=sa.text("'{}'::jsonb"),
    )
    op.alter_column(
        "shipment",
        "attributes",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
        existing_server_default=sa.text("'{}'::json"),  # type: ignore[arg-type]
        server_default=sa.text("'{}'::jsonb"),
    )

    op.alter_column(
        "sku",
        "attributes",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
        existing_server_default=sa.text("'{}'::json"),  # type: ignore[arg-type]
        server_default=sa.text("'{}'::jsonb"),
    )
    op.alter_column(
        "user",
        "attributes",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
        existing_server_default=sa.text("'{}'::json"),  # type: ignore[arg-type]
        server_default=sa.text("'{}'::jsonb"),
    )

    op.create_foreign_key(
        None,
        "billing",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
        use_alter=True,
    )
    op.create_foreign_key(
        None,
        "shipping",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
        use_alter=True,
    )
