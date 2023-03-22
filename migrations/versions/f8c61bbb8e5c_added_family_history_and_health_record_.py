"""added family history and health record models

Revision ID: f8c61bbb8e5c
Revises: ab58b988c581
Create Date: 2023-03-22 12:31:07.109722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8c61bbb8e5c'
down_revision = 'ab58b988c581'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('family_history_records',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('health_records',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('other_underlying_disease', sa.String(), nullable=True),
    sa.Column('other_family_disease', sa.String(), nullable=True),
    sa.Column('fasting_datetime', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('underlying_diseases',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('family_history_health_records',
    sa.Column('family_history_record_id', sa.Integer(), nullable=False),
    sa.Column('health_record_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['family_history_record_id'], ['family_history_records.id'], ),
    sa.ForeignKeyConstraint(['health_record_id'], ['health_records.id'], ),
    sa.PrimaryKeyConstraint('family_history_record_id', 'health_record_id')
    )
    op.create_table('underlying_diseases_health_records',
    sa.Column('disease_id', sa.Integer(), nullable=False),
    sa.Column('health_record_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['disease_id'], ['underlying_diseases.id'], ),
    sa.ForeignKeyConstraint(['health_record_id'], ['health_records.id'], ),
    sa.PrimaryKeyConstraint('disease_id', 'health_record_id')
    )
    with op.batch_alter_table('client_physical_profiles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('waist', sa.Numeric(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client_physical_profiles', schema=None) as batch_op:
        batch_op.drop_column('waist')

    op.drop_table('underlying_diseases_health_records')
    op.drop_table('family_history_health_records')
    op.drop_table('underlying_diseases')
    op.drop_table('health_records')
    op.drop_table('family_history_records')
    # ### end Alembic commands ###