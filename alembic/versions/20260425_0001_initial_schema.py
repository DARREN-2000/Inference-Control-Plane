"""initial schema

Revision ID: 20260425_0001
Revises:
Create Date: 2026-04-25 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260425_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_keys_key_hash"), "api_keys", ["key_hash"], unique=True)
    op.create_index(op.f("ix_api_keys_tenant_id"), "api_keys", ["tenant_id"], unique=False)

    op.create_table(
        "request_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("api_key_hash", sa.String(length=64), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("model_used", sa.String(length=128), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("tokens", sa.Integer(), nullable=False),
        sa.Column("cost", sa.Numeric(12, 6), nullable=False),
        sa.Column("cache_hit", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_request_logs_api_key_hash"), "request_logs", ["api_key_hash"], unique=False)
    op.create_index(op.f("ix_request_logs_created_at"), "request_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_request_logs_model_used"), "request_logs", ["model_used"], unique=False)
    op.create_index(op.f("ix_request_logs_status"), "request_logs", ["status"], unique=False)
    op.create_index(op.f("ix_request_logs_tenant_id"), "request_logs", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_request_logs_user_id"), "request_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_request_logs_user_id"), table_name="request_logs")
    op.drop_index(op.f("ix_request_logs_tenant_id"), table_name="request_logs")
    op.drop_index(op.f("ix_request_logs_status"), table_name="request_logs")
    op.drop_index(op.f("ix_request_logs_model_used"), table_name="request_logs")
    op.drop_index(op.f("ix_request_logs_created_at"), table_name="request_logs")
    op.drop_index(op.f("ix_request_logs_api_key_hash"), table_name="request_logs")
    op.drop_table("request_logs")

    op.drop_index(op.f("ix_api_keys_tenant_id"), table_name="api_keys")
    op.drop_index(op.f("ix_api_keys_key_hash"), table_name="api_keys")
    op.drop_table("api_keys")
