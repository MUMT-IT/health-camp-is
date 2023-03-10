"""added Client model

Revision ID: 1affa7e409b1
Revises: 
Create Date: 2023-03-10 08:48:02.569670

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1affa7e409b1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clients',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('firstname', sa.String(), nullable=False),
    sa.Column('lastname', sa.String(), nullable=False),
    sa.Column('pid', sa.String(length=13), nullable=True),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.Column('client_number', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('clients')
    # ### end Alembic commands ###
