"""add is admin to user

Revision ID: 4f27a9c1d8e0
Revises: 132d570d7266
"""

from alembic import op
import sqlalchemy as sa


revision = "4f27a9c1d8e0"
down_revision = "132d570d7266"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade():
    op.drop_column("user", "is_admin")
