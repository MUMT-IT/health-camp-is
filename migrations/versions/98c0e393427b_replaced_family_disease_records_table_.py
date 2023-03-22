"""replaced family disease records table with family diseases

Revision ID: 98c0e393427b
Revises: f8c61bbb8e5c
Create Date: 2023-03-22 12:42:29.796691

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98c0e393427b'
down_revision = 'f8c61bbb8e5c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('family_diseases',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('family_diseases_health_records',
    sa.Column('family_history_record_id', sa.Integer(), nullable=False),
    sa.Column('health_record_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['family_history_record_id'], ['family_diseases.id'], ),
    sa.ForeignKeyConstraint(['health_record_id'], ['health_records.id'], ),
    sa.PrimaryKeyConstraint('family_history_record_id', 'health_record_id')
    )
    op.drop_table('family_history_health_records')
    op.drop_table('family_history_records')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('family_history_records',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('family_history_records_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='family_history_records_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('family_history_health_records',
    sa.Column('family_history_record_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('health_record_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['family_history_record_id'], ['family_history_records.id'], name='family_history_health_records_family_history_record_id_fkey'),
    sa.ForeignKeyConstraint(['health_record_id'], ['health_records.id'], name='family_history_health_records_health_record_id_fkey'),
    sa.PrimaryKeyConstraint('family_history_record_id', 'health_record_id', name='family_history_health_records_pkey')
    )
    op.drop_table('family_diseases_health_records')
    op.drop_table('family_diseases')
    # ### end Alembic commands ###
