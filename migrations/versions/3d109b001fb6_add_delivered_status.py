"""add delivered status

Revision ID: 3d109b001fb6
Revises: 0eaad6ff6f52
Create Date: 2026-03-07 15:34:20.642310
"""

from alembic import op
import sqlalchemy as sa


revision = '3d109b001fb6'
down_revision = '0eaad6ff6f52'
branch_labels = None
depends_on = None


def upgrade():

    # thêm DELIVERED vào enum order_status
    op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'DELIVERED'")

    # tạo enum product_status nếu chưa tồn tại
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'product_status') THEN
            CREATE TYPE product_status AS ENUM ('ACTIVE','HIDDEN','DELETED');
        END IF;
    END$$;
    """)

    # BƯỚC 1: bỏ default
    op.execute("""
    ALTER TABLE products
    ALTER COLUMN status DROP DEFAULT
    """)

    # BƯỚC 2: đổi type
    op.execute("""
    ALTER TABLE products
    ALTER COLUMN status TYPE product_status
    USING status::product_status
    """)

    # BƯỚC 3: set lại default
    op.execute("""
    ALTER TABLE products
    ALTER COLUMN status SET DEFAULT 'ACTIVE'
    """)

    # BƯỚC 4: set NOT NULL
    op.execute("""
    ALTER TABLE products
    ALTER COLUMN status SET NOT NULL
    """)


def downgrade():

    op.execute("""
    ALTER TABLE products
    ALTER COLUMN status TYPE VARCHAR(20)
    """)