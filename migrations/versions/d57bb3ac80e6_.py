"""empty message

Revision ID: d57bb3ac80e6
Revises: 225f57dd9b55
Create Date: 2023-12-30 13:01:07.830927

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd57bb3ac80e6'
down_revision = '225f57dd9b55'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('warehouseupdate', schema=None) as batch_op:
        batch_op.drop_column('total_cost_price')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('warehouseupdate', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_cost_price', mysql.FLOAT(), nullable=False))

    # ### end Alembic commands ###
