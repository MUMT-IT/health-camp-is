"""added client address model

Revision ID: 02800049a8c7
Revises: c20fd378268d
Create Date: 2023-03-26 00:17:39.113395

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02800049a8c7'
down_revision = 'c20fd378268d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('client_addresses',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'client_addresses', ['address_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('address_id')

    op.drop_table('client_addresses')
    # ### end Alembic commands ###
