"""add product status for soft delete

Revision ID: a1b2c3d4e5f6
Revises: 5d8aad89768e
Create Date: 2026-03-07 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '5d8aad89768e'
branch_labels = None
depends_on = None

product_status_enum = sa.Enum('ACTIVE', 'HIDDEN', 'DELETED', name='product_status')


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    product_status_enum.create(bind, checkfirst=True)

    columns = [c['name'] for c in inspector.get_columns('products')]

    with op.batch_alter_table('products', schema=None) as batch_op:
        if 'status' not in columns:
            batch_op.add_column(
                sa.Column(
                    'status',
                    product_status_enum,
                    nullable=False,
                    server_default='ACTIVE'
                )
            )

        batch_op.create_index(
            batch_op.f('ix_products_status'),
            ['status'],
            unique=False
        )


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [c['name'] for c in inspector.get_columns('products')]

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_products_status'))

        if 'status' in columns:
            batch_op.drop_column('status')

    product_status_enum.drop(bind, checkfirst=True)