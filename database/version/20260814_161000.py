from alembic import op

revision = "6a4f8c2d1e90"
down_revision = "9c5c0eb851a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "sitemap_image",
        "sitemap_location_id",
        new_column_name="location_id",
    )


def downgrade() -> None:
    op.alter_column(
        "sitemap_image",
        "location_id",
        new_column_name="sitemap_location_id",
    )
