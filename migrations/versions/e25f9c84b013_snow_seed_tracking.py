"""Track one-time public weather dataset imports."""
from alembic import op
import sqlalchemy as sa

revision = 'e25f9c84b013'
down_revision = 'd14e8b73a902'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('snow_seed_runs',
        sa.Column('digest', sa.String(64), primary_key=True),
        sa.Column('applied_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))


def downgrade():
    op.drop_table('snow_seed_runs')
