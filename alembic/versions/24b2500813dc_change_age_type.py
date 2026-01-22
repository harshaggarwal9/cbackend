from alembic import op


def upgrade():
    op.execute(
        """
        ALTER TABLE public.users
        ALTER COLUMN agename
        TYPE VARCHAR
        USING agename::varchar
        """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE public.users
        ALTER COLUMN agename
        TYPE INTEGER
        USING agename::integer
        """
    )
