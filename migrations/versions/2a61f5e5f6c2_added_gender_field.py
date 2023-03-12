"""added gender field

Revision ID: 2a61f5e5f6c2
Revises: 0e0b6f44258e
Create Date: 2023-03-12 13:40:00.668147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a61f5e5f6c2'
down_revision = '0e0b6f44258e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gender', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.drop_column('gender')

    # ### end Alembic commands ###
