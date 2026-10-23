"""Private positioning diagnostics and sanitized public snapshots."""
from alembic import op
import sqlalchemy as sa
revision = '2a6ea90e4b52'
down_revision = 'e25f9c84b013'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('positioning_diagnostics',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=160), nullable=False),
        sa.Column('role', sa.String(length=40), nullable=False),
        sa.Column('context', sa.Text(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table('positioning_profiles',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('diagnostic_id', sa.String(length=36), sa.ForeignKey('positioning_diagnostics.id'), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('kind', sa.String(length=20), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=False),
    )
    op.create_table('positioning_assessments',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('profile_id', sa.String(length=36), sa.ForeignKey('positioning_profiles.id'), nullable=False),
        sa.Column('criterion', sa.String(length=60), nullable=False),
        sa.Column('finding', sa.Text(), nullable=False),
        sa.Column('confidence', sa.String(length=10), nullable=False),
        sa.Column('confidence_reason', sa.Text(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('excerpt', sa.Text(), nullable=False),
        sa.Column('consulted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by', sa.String(length=160), nullable=True),
        sa.UniqueConstraint("profile_id", "criterion"),
    )
    op.create_table('positioning_snapshots',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('diagnostic_id', sa.String(length=36), sa.ForeignKey('positioning_diagnostics.id'), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('provenance', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    )

def downgrade():
    op.drop_table('positioning_snapshots')
    op.drop_table('positioning_assessments')
    op.drop_table('positioning_profiles')
    op.drop_table('positioning_diagnostics')
