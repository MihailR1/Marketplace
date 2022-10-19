"""Shopping Cart Model

Revision ID: aa5201575d6c
Revises: 67a4bced704b
Create Date: 2022-10-16 16:36:26.735113

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa5201575d6c'
down_revision = '67a4bced704b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shopping_cart',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('product', sa.Column('quantity', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_product_quantity'), 'product', ['quantity'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_product_quantity'), table_name='product')
    op.drop_column('product', 'quantity')
    op.drop_table('shopping_cart')
    # ### end Alembic commands ###
