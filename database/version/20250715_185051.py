from difflib import SequenceMatcher
from enum import StrEnum
from typing import TypedDict

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

from web.database.model import (
    Base,
    EmailStatus,
    EmailStatusId,
    FileType,
    FileTypeId,
    OrderStatus,
    OrderStatusId,
    ProductLinkType,
    ProductLinkTypeId,
    ProductType,
    ProductTypeId,
    UserRole,
    UserRoleId,
)

revision = "20250715_185051"
down_revision = "577c6a34b207"
branch_labels = None
depends_on = None


def similarity(a, b) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


class TableData(TypedDict):
    table: type[Base]
    table_name: str
    cur_type: type[sa.Integer]
    new_type: sa.VARCHAR
    foreign_keys: list[dict[str, str]]
    enum: type[StrEnum]


data: list[TableData] = [
    {
        "table": EmailStatus,
        "table_name": "email_status",
        "cur_type": sa.Integer,
        "new_type": sa.VARCHAR(length=32),
        "foreign_keys": [{"table_name": "email", "column_name": "status_id"}],
        "enum": EmailStatusId,
    },
    {
        "table": FileType,
        "table_name": "file_type",
        "cur_type": sa.Integer,
        "new_type": sa.VARCHAR(length=32),
        "foreign_keys": [{"table_name": "file", "column_name": "type_id"}],
        "enum": FileTypeId,
    },
    {
        "table": OrderStatus,
        "table_name": "order_status",
        "cur_type": sa.Integer,
        "new_type": sa.VARCHAR(length=32),
        "foreign_keys": [{"table_name": "order", "column_name": "status_id"}],
        "enum": OrderStatusId,
    },
    {
        "table": ProductLinkType,
        "table_name": "product_link_type",
        "cur_type": sa.Integer,
        "new_type": sa.VARCHAR(length=32),
        "foreign_keys": [{"table_name": "product_link", "column_name": "type_id"}],
        "enum": ProductLinkTypeId,
    },
    {
        "table": ProductType,
        "table_name": "product_type",
        "cur_type": sa.Integer,
        "new_type": sa.VARCHAR(length=32),
        "foreign_keys": [{"table_name": "product", "column_name": "type_id"}],
        "enum": ProductTypeId,
    },
    {
        "table": UserRole,
        "table_name": "user_role",
        "cur_type": sa.Integer,
        "new_type": sa.VARCHAR(length=32),
        "foreign_keys": [{"table_name": "user", "column_name": "role_id"}],
        "enum": UserRoleId,
    },
]


def upgrade() -> None:
    for table in data:
        cls_ = table["table"]
        table_name = table["table_name"]
        table_index = f"{table_name}_pkey"
        table_sequence = f"{table_name}_id_seq"
        col_cur_type = table["cur_type"]
        col_new_type = table["new_type"]
        foreign_keys = table["foreign_keys"]
        enum = table["enum"]

        # Drop primary key constraint
        op.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {table_index} CASCADE")
        op.execute(f"DROP SEQUENCE IF EXISTS {table_sequence} CASCADE")

        # Change primary key type
        op.alter_column(
            table_name,
            "id",
            existing_type=col_cur_type,
            type_=col_new_type,
        )
        for fk in foreign_keys:
            fk_table_name = fk["table_name"]
            fk_column_name = fk["column_name"]
            op.alter_column(
                fk_table_name,
                fk_column_name,
                existing_type=col_cur_type,
                type_=col_new_type,
            )

        # Recreate the primary key constraint
        op.create_primary_key(table_index, table_name, ["id"])

        # Recreate the foreign key constraint
        for fk in foreign_keys:
            fk_table_name = fk["table_name"]
            fk_column_name = fk["column_name"]
            fk_table_index = f"{fk_table_name}_{fk_column_name}_fkey"
            op.create_foreign_key(
                fk_table_index,
                fk_table_name,
                table_name,
                [fk_column_name],
                ["id"],
                ondelete="RESTRICT",
                onupdate="CASCADE",
            )

        # Update table values
        bind = op.get_bind()
        s = orm.Session(bind=bind)
        for row in s.query(cls_).all():
            for item in enum:
                score = similarity(row.name, item.value)  # type: ignore[attr-defined]
                if score > 0.8:
                    row.id = item.value  # type: ignore[attr-defined]
                    break
        s.flush()

    # Additional operations
    op.alter_column(
        "email",
        "status_id",
        existing_type=sa.VARCHAR(length=32),
        server_default=None,
        existing_nullable=False,
    )
