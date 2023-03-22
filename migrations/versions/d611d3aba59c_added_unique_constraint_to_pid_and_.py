"""added unique constraint to pid and client number

Revision ID: d611d3aba59c
Revises: 2a67bc9ec1ba
Create Date: 2023-03-22 17:12:12.817072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd611d3aba59c'
down_revision = '2a67bc9ec1ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['client_number'])
        batch_op.create_unique_constraint(None, ['pid'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###
