"""empty message

Revision ID: e8a353616ea4
Revises: 11589bd00cd2
Create Date: 2023-12-30 10:49:45.884464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8a353616ea4'
down_revision = '11589bd00cd2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('warehouseupdate', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_cost_price', sa.Float(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('warehouseupdate', schema=None) as batch_op:
        batch_op.drop_column('total_cost_price')

    # ### end Alembic commands ###
