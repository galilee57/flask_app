"""add snake stats

Revision ID: cbc0323bbb56
Revises: 2723ded5d35c
Create Date: 2026-06-20 19:01:41.676361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbc0323bbb56'
down_revision = '2723ded5d35c'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if 'snake_stats' not in table_names:
        op.create_table('snake_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mode', sa.String(length=20), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('steps_since_fruit', sa.Integer(), nullable=False),
        sa.Column('total_steps', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )

    columns = {column['name']: column for column in inspector.get_columns('programme_exercices')}
    with op.batch_alter_table('programme_exercices', schema=None) as batch_op:
        if not isinstance(columns['exercice_id']['type'], sa.String):
            batch_op.alter_column('exercice_id',
                   existing_type=columns['exercice_id']['type'],
                   type_=sa.String(length=200),
                   existing_nullable=False)
        if 'exercice_name' in columns:
            batch_op.drop_column('exercice_name')


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column['name']: column for column in inspector.get_columns('programme_exercices')}

    with op.batch_alter_table('programme_exercices', schema=None) as batch_op:
        if 'exercice_name' not in columns:
            batch_op.add_column(sa.Column('exercice_name', sa.String(length=200), nullable=True))
        if not isinstance(columns['exercice_id']['type'], sa.Integer):
            batch_op.alter_column('exercice_id',
                   existing_type=columns['exercice_id']['type'],
                   type_=sa.Integer(),
                   existing_nullable=False)

    if 'snake_stats' in inspector.get_table_names():
        op.drop_table('snake_stats')
