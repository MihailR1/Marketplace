"""change category, product models

Revision ID: 67a4bced704b
Revises: dc6b795abead
Create Date: 2022-10-14 12:15:44.960682

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67a4bced704b'
down_revision = 'dc6b795abead'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('product', 'name',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=180),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('product', 'name',
               existing_type=sa.String(length=180),
               type_=sa.VARCHAR(length=120),
               existing_nullable=False)
    # ### end Alembic commands ###
