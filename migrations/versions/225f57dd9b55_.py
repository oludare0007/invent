"""empty message

Revision ID: 225f57dd9b55
Revises: 27a181f20538
Create Date: 2023-12-30 12:17:04.867884

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '225f57dd9b55'
down_revision = '27a181f20538'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('warehouseupdate', schema=None) as batch_op:
        batch_op.drop_column('total_productqty')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('warehouseupdate', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_productqty', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
