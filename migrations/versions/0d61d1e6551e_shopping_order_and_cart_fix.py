"""shopping order and cart fix

Revision ID: 0d61d1e6551e
Revises: 90db7c3e5dbd
Create Date: 2022-10-30 14:39:19.435933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d61d1e6551e'
down_revision = '90db7c3e5dbd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shopping_cart', sa.Column('order_id', sa.Integer(), nullable=True))
    op.add_column('shopping_cart', sa.Column('is_shopping_cart_paid', sa.Boolean(), nullable=True))
    op.add_column('shopping_cart', sa.Column('creation_datetime', sa.DateTime(), nullable=True))
    op.drop_constraint('shopping_cart_user_id_fkey', 'shopping_cart', type_='foreignkey')
    op.drop_constraint('shopping_cart_product_id_fkey', 'shopping_cart', type_='foreignkey')
    op.create_foreign_key(None, 'shopping_cart', 'product', ['product_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'shopping_cart', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'shopping_cart', 'shopping_order', ['order_id'], ['id'], ondelete='CASCADE')
    op.add_column('shopping_order', sa.Column('order_number', sa.String(length=90), nullable=True))
    op.add_column('shopping_order', sa.Column('paid_datetime', sa.DateTime(), nullable=True))
    op.drop_constraint('shopping_order_user_id_fkey', 'shopping_order', type_='foreignkey')
    op.create_foreign_key(None, 'shopping_order', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_column('shopping_order', 'order_id')
    op.add_column('user', sa.Column('registration_datetime', sa.DateTime(), nullable=True))
    op.alter_column('user', 'role',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.Enum('admin', 'user', name='userrole'),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'role',
               existing_type=sa.Enum('admin', 'user', name='userrole'),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)
    op.drop_column('user', 'registration_datetime')
    op.add_column('shopping_order', sa.Column('order_id', sa.VARCHAR(length=90), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'shopping_order', type_='foreignkey')
    op.create_foreign_key('shopping_order_user_id_fkey', 'shopping_order', 'user', ['user_id'], ['id'])
    op.drop_column('shopping_order', 'paid_datetime')
    op.drop_column('shopping_order', 'order_number')
    op.drop_constraint(None, 'shopping_cart', type_='foreignkey')
    op.drop_constraint(None, 'shopping_cart', type_='foreignkey')
    op.drop_constraint(None, 'shopping_cart', type_='foreignkey')
    op.create_foreign_key('shopping_cart_product_id_fkey', 'shopping_cart', 'product', ['product_id'], ['id'])
    op.create_foreign_key('shopping_cart_user_id_fkey', 'shopping_cart', 'user', ['user_id'], ['id'])
    op.drop_column('shopping_cart', 'creation_datetime')
    op.drop_column('shopping_cart', 'is_shopping_cart_paid')
    op.drop_column('shopping_cart', 'order_id')
    # ### end Alembic commands ###
