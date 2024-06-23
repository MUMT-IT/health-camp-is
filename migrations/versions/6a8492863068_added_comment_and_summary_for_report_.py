"""added comment and summary for report and report item models

Revision ID: 6a8492863068
Revises: 0bcd63550edb
Create Date: 2023-10-31 05:27:49.658863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a8492863068'
down_revision = '0bcd63550edb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stool_test_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('summary', sa.Text(), nullable=True))

    with op.batch_alter_table('stool_test_report_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comment', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stool_test_report_items', schema=None) as batch_op:
        batch_op.drop_column('comment')

    with op.batch_alter_table('stool_test_records', schema=None) as batch_op:
        batch_op.drop_column('summary')

    # ### end Alembic commands ###