import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "5b9b2787f4a1"
down_revision = "b1f4d2c8a901"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "app_route",
        sa.Column("template_path", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "app_route",
        sa.Column(
            "sitemap_group",
            sa.String(length=32),
            server_default="pages",
            nullable=False,
        ),
    )
    op.create_table(
        "sitemap_location",
        sa.Column(
            "endpoint_args",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("lastmod", sa.DateTime(timezone=True), nullable=False),
        sa.Column("template_hash", sa.String(length=64), nullable=True),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["route_id"], ["app_route.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("route_id", "endpoint_args"),
    )
    op.execute(
        """
        INSERT INTO sitemap_location (route_id, endpoint_args, lastmod)
        SELECT id, '{}'::jsonb,
               COALESCE(GREATEST(created_at, updated_at), updated_at, created_at, now())
        FROM app_route
        WHERE in_sitemap = true AND is_collection = false
        """
    )
    op.execute(
        """
        INSERT INTO sitemap_location (route_id, endpoint_args, lastmod)
        SELECT
            route.id,
            jsonb_build_object(route.sitemap_query_key, value),
            COALESCE(GREATEST(route.created_at, route.updated_at),
                     route.updated_at, route.created_at, now())
        FROM app_route AS route
        CROSS JOIN LATERAL unnest(route.sitemap_query_values) AS value
        WHERE route.in_sitemap = true
          AND route.is_collection = true
          AND route.sitemap_query_key IS NOT NULL
          AND route.sitemap_query_values IS NOT NULL
        """
    )
    op.drop_column("app_route", "sitemap_query_values")
    op.drop_column("app_route", "sitemap_query_key")


def downgrade() -> None:
    op.add_column(
        "app_route",
        sa.Column("sitemap_query_key", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "app_route",
        sa.Column("sitemap_query_values", postgresql.ARRAY(sa.Text()), nullable=True),
    )
    op.drop_table("sitemap_location")
    op.drop_column("app_route", "sitemap_group")
    op.drop_column("app_route", "template_path")
