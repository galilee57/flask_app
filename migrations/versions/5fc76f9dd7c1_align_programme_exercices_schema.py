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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"]: column for column in inspector.get_columns("programme_exercices")}
    constraints = {
        constraint["name"]
        for constraint in inspector.get_check_constraints("programme_exercices")
    }

    with op.batch_alter_table("programme_exercices", schema=None) as batch_op:
        if not isinstance(columns["exercice_id"]["type"], sa.String):
            batch_op.alter_column(
                "exercice_id",
                existing_type=columns["exercice_id"]["type"],
                type_=sa.String(length=200),
                existing_nullable=False,
            )
        if "exercice_name" in columns:
            batch_op.drop_column("exercice_name")
        if "ck_programme_exercices_reps_positive" not in constraints:
            batch_op.create_check_constraint("ck_programme_exercices_reps_positive", "reps > 0")
        if "ck_programme_exercices_weight_nonnegative" not in constraints:
            batch_op.create_check_constraint("ck_programme_exercices_weight_nonnegative", "weight >= 0")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"]: column for column in inspector.get_columns("programme_exercices")}
    constraints = {
        constraint["name"]
        for constraint in inspector.get_check_constraints("programme_exercices")
    }

    with op.batch_alter_table("programme_exercices", schema=None) as batch_op:
        if "ck_programme_exercices_weight_nonnegative" in constraints:
            batch_op.drop_constraint("ck_programme_exercices_weight_nonnegative", type_="check")
        if "ck_programme_exercices_reps_positive" in constraints:
            batch_op.drop_constraint("ck_programme_exercices_reps_positive", type_="check")
        if "exercice_name" not in columns:
            batch_op.add_column(sa.Column("exercice_name", sa.String(length=200), nullable=True))
        if not isinstance(columns["exercice_id"]["type"], sa.Integer):
            batch_op.alter_column(
                "exercice_id",
                existing_type=columns["exercice_id"]["type"],
                type_=sa.Integer(),
                existing_nullable=False,
            )
