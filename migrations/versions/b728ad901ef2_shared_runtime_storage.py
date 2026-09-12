"""Add shared tasks, patterns and server-side sessions."""
from alembic import op
import sqlalchemy as sa

revision = "b728ad901ef2"
down_revision = "9ad4c7e0b812"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("todo", sa.Column("id", sa.String(36), primary_key=True),
                    sa.Column("text", sa.Text(), nullable=False),
                    sa.Column("done", sa.Boolean(), nullable=False),
                    sa.Column("created_at", sa.String(40), nullable=False))
    op.create_table("saved_pattern", sa.Column("name", sa.String(80), primary_key=True),
                    sa.Column("payload", sa.JSON(), nullable=False))
    op.create_table("runtime_session", sa.Column("id", sa.String(64), primary_key=True),
                    sa.Column("payload", sa.Text(), nullable=False),
                    sa.Column("expires_at", sa.BigInteger(), nullable=False),
                    sa.Column("version", sa.Integer(), nullable=False))
    op.create_index("ix_runtime_session_expires_at", "runtime_session", ["expires_at"])


def downgrade():
    op.drop_index("ix_runtime_session_expires_at", table_name="runtime_session")
    op.drop_table("runtime_session")
    op.drop_table("saved_pattern")
    op.drop_table("todo")
