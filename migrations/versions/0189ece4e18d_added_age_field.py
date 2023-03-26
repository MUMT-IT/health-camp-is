"""added age field

Revision ID: 0189ece4e18d
Revises: 1862a0ba3b80
Create Date: 2023-03-26 11:16:31.822928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0189ece4e18d'
down_revision = '1862a0ba3b80'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('age', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.drop_column('age')
