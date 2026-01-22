"""change age type

Revision ID: d212ae779eb5
Revises: 9224bd356305
Create Date: 2026-01-15 19:05:24.207351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd212ae779eb5'
down_revision: Union[str, Sequence[str], None] = '9224bd356305'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # INTEGER → STRING
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN agename
        TYPE VARCHAR
        USING agename::varchar
        """
    )


def downgrade():
    # STRING → INTEGER (rollback)
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN agename
        TYPE INTEGER
        USING agename::integer
        """
    )
