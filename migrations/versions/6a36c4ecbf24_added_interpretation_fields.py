"""added interpretation fields

Revision ID: 6a36c4ecbf24
Revises: d611d3aba59c
Create Date: 2023-03-25 11:30:24.351391

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a36c4ecbf24'
down_revision = 'd611d3aba59c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('min_interpret', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('max_interpret', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tests', schema=None) as batch_op:
        batch_op.drop_column('max_interpret')
        batch_op.drop_column('min_interpret')

    # ### end Alembic commands ###