"""Store completed Snake games separately from legacy per-fruit statistics."""
from alembic import op
import sqlalchemy as sa

revision = "c90f214e7a31"
down_revision = "b728ad901ef2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "snake_result",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("total_steps", sa.Integer(), nullable=False),
        sa.Column("end_reason", sa.String(40), nullable=False),
        sa.Column("seed", sa.Integer()),
        sa.Column("model_hash", sa.String(64)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table("snake_result")
