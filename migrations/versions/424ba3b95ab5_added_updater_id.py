"""added updater ID

Revision ID: 424ba3b95ab5
Revises: 0189ece4e18d
Create Date: 2023-03-26 11:42:18.157077

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '424ba3b95ab5'
down_revision = '0189ece4e18d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('health_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updater_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['updater_id'], ['id'])

    with op.batch_alter_table('test_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updater_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['updater_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_records', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('updater_id')

    with op.batch_alter_table('health_records', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('updater_id')

    # ### end Alembic commands ###
