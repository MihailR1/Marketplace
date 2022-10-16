"""merge 5f92b71173a5 and 67a4bced704b

Revision ID: 0911480e14ae
Revises: 5f92b71173a5, 67a4bced704b
Create Date: 2022-10-15 14:39:56.792348

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0911480e14ae'
down_revision = ('5f92b71173a5', '67a4bced704b')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
