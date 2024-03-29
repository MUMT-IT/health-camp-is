"""added email field

Revision ID: 242e714b5af2
Revises: dc256d5e827a
Create Date: 2023-03-25 23:14:59.053854

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '242e714b5af2'
down_revision = 'dc256d5e827a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('email')

    # ### end Alembic commands ###
