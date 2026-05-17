"""Crear esquema inicial

Revision ID: 202605151936
Revises:
Create Date: 2026-05-15 19:36:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "202605151936"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("brand", sa.String(length=80), nullable=False),
        sa.Column("arrival_location", sa.String(length=120), nullable=False),
        sa.Column("applicant_name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vehicles_brand"), "vehicles", ["brand"], unique=False)
    op.create_index(op.f("ix_vehicles_id"), "vehicles", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_vehicles_id"), table_name="vehicles")
    op.drop_index(op.f("ix_vehicles_brand"), table_name="vehicles")
    op.drop_table("vehicles")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
