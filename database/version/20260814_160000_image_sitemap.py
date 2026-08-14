import sqlalchemy as sa
from alembic import op

revision = "9c5c0eb851a7"
down_revision = "5b9b2787f4a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "app_route",
        sa.Column("sitemap_image_mode", sa.String(length=16), nullable=True),
    )
    op.create_table(
        "sitemap_image",
        sa.Column("loc", sa.String(length=2048), nullable=False),
        sa.Column("sitemap_location_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["sitemap_location_id"],
            ["sitemap_location.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sitemap_location_id", "loc"),
    )


def downgrade() -> None:
    op.drop_table("sitemap_image")
    op.drop_column("app_route", "sitemap_image_mode")
