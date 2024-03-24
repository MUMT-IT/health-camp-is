"""added is_quantitative field

Revision ID: 2bce9c1b4725
Revises: d64d1f5e61c3
Create Date: 2024-03-24 12:13:37.596144

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bce9c1b4725'
down_revision = 'd64d1f5e61c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_quantitative', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_records', schema=None) as batch_op:
        batch_op.drop_column('is_quantitative')

    # ### end Alembic commands ###
