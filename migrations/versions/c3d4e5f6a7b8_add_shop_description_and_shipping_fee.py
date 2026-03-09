"""add shop description and shipping fee

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-07 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('shops', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('shipping_fee', sa.Numeric(precision=12, scale=2), nullable=True, server_default='0'))


def downgrade():
    with op.batch_alter_table('shops', schema=None) as batch_op:
        batch_op.drop_column('shipping_fee')
        batch_op.drop_column('description')