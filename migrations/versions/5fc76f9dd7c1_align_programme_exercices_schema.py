"""Align programme_exercices with the SQLAlchemy model.

Revision ID: 5fc76f9dd7c1
Revises: 2723ded5d35c
"""

from alembic import op
import sqlalchemy as sa


revision = "5fc76f9dd7c1"
down_revision = "2723ded5d35c"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("programme_exercices", schema=None) as batch_op:
        batch_op.alter_column(
            "exercice_id",
            existing_type=sa.Integer(),
            type_=sa.String(length=200),
            existing_nullable=False,
        )
        batch_op.drop_column("exercice_name")
        batch_op.create_check_constraint("ck_programme_exercices_reps_positive", "reps > 0")
        batch_op.create_check_constraint("ck_programme_exercices_weight_nonnegative", "weight >= 0")


def downgrade():
    with op.batch_alter_table("programme_exercices", schema=None) as batch_op:
        batch_op.drop_constraint("ck_programme_exercices_weight_nonnegative", type_="check")
        batch_op.drop_constraint("ck_programme_exercices_reps_positive", type_="check")
        batch_op.add_column(sa.Column("exercice_name", sa.String(length=200), nullable=True))
        batch_op.alter_column(
            "exercice_id",
            existing_type=sa.String(length=200),
            type_=sa.Integer(),
            existing_nullable=False,
        )
