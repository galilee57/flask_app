"""Add normalized Snow Layers history to the shared database."""
from alembic import op
import sqlalchemy as sa

revision = "d14e8b73a902"
down_revision = "c90f214e7a31"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("snow_stations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(80), nullable=False, unique=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("elevation_m", sa.Float(), nullable=False))
    op.create_table("snow_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True))
    op.create_table("snow_imports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("snow_sources.id"), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=False),
        sa.Column("imported_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("source_id", "source_url", "imported_at", name="uq_snow_import_provenance"),
        sa.UniqueConstraint("id", "source_id", name="uq_snow_import_source"))
    op.create_table("snow_daily_observations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("station_id", sa.Integer(), sa.ForeignKey("snow_stations.id"), nullable=False),
        sa.Column("observed_on", sa.Date(), nullable=False),
        sa.Column("snow_depth_cm", sa.Float(), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("snow_sources.id"), nullable=False),
        sa.Column("import_id", sa.Integer(), nullable=False),
        sa.UniqueConstraint("station_id", "observed_on", "source_id", name="uq_snow_daily_station_date_source"),
        sa.ForeignKeyConstraint(["import_id", "source_id"], ["snow_imports.id", "snow_imports.source_id"], name="fk_snow_daily_import_source"))
    op.create_index("ix_snow_daily_observations_observed_on", "snow_daily_observations", ["observed_on"])


def downgrade():
    op.drop_table("snow_daily_observations")
    op.drop_table("snow_imports")
    op.drop_table("snow_sources")
    op.drop_table("snow_stations")
