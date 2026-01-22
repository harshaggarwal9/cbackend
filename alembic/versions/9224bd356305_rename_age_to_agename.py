"""rename age to agename

Revision ID: 9224bd356305
Revises: 281906289a09
Create Date: 2026-01-15 18:45:32.123485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9224bd356305'
down_revision: Union[str, Sequence[str], None] = '281906289a09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("users", "age", new_column_name="agename")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("users", "agename", new_column_name="age")
