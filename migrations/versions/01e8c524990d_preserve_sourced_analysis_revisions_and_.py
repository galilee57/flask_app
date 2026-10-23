"""Preserve sourced analysis revisions and working memory."""
from alembic import op
import sqlalchemy as sa
revision = '01e8c524990d'
down_revision = '2a6ea90e4b52'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('positioning_analysis_runs',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('diagnostic_id', sa.String(length=36), sa.ForeignKey('positioning_diagnostics.id'), nullable=False),
        sa.Column('parent_id', sa.String(length=36), sa.ForeignKey('positioning_analysis_runs.id'), nullable=True),
        sa.Column('import_key', sa.String(length=160), nullable=False, unique=True),
        sa.Column('payload_hash', sa.String(length=64), nullable=False),
        sa.Column('memory_entry_ids', sa.JSON(), nullable=False),
        sa.Column('actor', sa.String(length=160), nullable=False),
        sa.Column('rubric', sa.JSON(), nullable=False),
        sa.Column('summary', sa.JSON(), nullable=False),
        sa.Column('limitations', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table('positioning_portfolio_reviews',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('run_id', sa.String(length=36), sa.ForeignKey('positioning_analysis_runs.id'), nullable=False),
        sa.Column('profile_id', sa.String(length=36), sa.ForeignKey('positioning_profiles.id'), nullable=False),
        sa.Column('origin_url', sa.Text(), nullable=False),
        sa.Column('role_label', sa.String(length=160), nullable=False),
        sa.Column('comparability', sa.String(length=20), nullable=False),
        sa.Column('scope', sa.Text(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=False),
        sa.UniqueConstraint('run_id', 'profile_id'),
    )
    op.create_table('positioning_review_observations',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('review_id', sa.String(length=36), sa.ForeignKey('positioning_portfolio_reviews.id'), nullable=False),
        sa.Column('criterion', sa.String(length=60), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('finding', sa.JSON(), nullable=False),
        sa.Column('confidence', sa.String(length=10), nullable=False),
        sa.Column('confidence_reason', sa.JSON(), nullable=False),
        sa.Column('source_keys', sa.JSON(), nullable=False),
        sa.UniqueConstraint('review_id', 'criterion'),
    )
    op.create_table('positioning_work_items',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('diagnostic_id', sa.String(length=36), sa.ForeignKey('positioning_diagnostics.id'), nullable=False),
        sa.Column('criterion', sa.String(length=60), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table('positioning_memory_entries',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('diagnostic_id', sa.String(length=36), sa.ForeignKey('positioning_diagnostics.id'), nullable=False),
        sa.Column('run_id', sa.String(length=36), sa.ForeignKey('positioning_analysis_runs.id'), nullable=True),
        sa.Column('work_item_id', sa.String(length=36), sa.ForeignKey('positioning_work_items.id'), nullable=True),
        sa.Column('criterion', sa.String(length=60), nullable=True),
        sa.Column('kind', sa.String(length=20), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('actor', sa.String(length=160), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

def downgrade():
    op.drop_table('positioning_memory_entries')
    op.drop_table('positioning_work_items')
    op.drop_table('positioning_review_observations')
    op.drop_table('positioning_portfolio_reviews')
    op.drop_table('positioning_analysis_runs')
