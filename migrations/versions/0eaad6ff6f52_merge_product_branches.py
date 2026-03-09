"""merge product branches

Revision ID: 0eaad6ff6f52
Revises: 41bf14fe284a, c3d4e5f6a7b8
Create Date: 2026-03-07 15:18:20.674758

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0eaad6ff6f52'
down_revision = ('41bf14fe284a', 'c3d4e5f6a7b8')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
