"""checkout cart

Revision ID: 90db7c3e5dbd
Revises: ebf855e60715
Create Date: 2022-10-28 17:07:19.995737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90db7c3e5dbd'
down_revision = 'ebf855e60715'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('shopping_order_shopping_cart_id_fkey', 'shopping_order', type_='foreignkey')
    op.drop_column('shopping_order', 'shopping_cart_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shopping_order', sa.Column('shopping_cart_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('shopping_order_shopping_cart_id_fkey', 'shopping_order', 'shopping_cart', ['shopping_cart_id'], ['id'])
    # ### end Alembic commands ###
