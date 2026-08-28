"""Merge the Snake statistics and programme-schema migration branches.

Revision ID: 9ad4c7e0b812
Revises: 5fc76f9dd7c1, cbc0323bbb56
"""

# revision identifiers, used by Alembic.
revision = "9ad4c7e0b812"
down_revision = ("5fc76f9dd7c1", "cbc0323bbb56")
branch_labels = None
depends_on = None


def upgrade():
    """The branch migrations contain all schema operations."""


def downgrade():
    """Alembic restores the two parent heads when leaving this merge point."""
