"""Class Category and Product

Revision ID: 7b6fcd8acd5a
Revises: 9328971a22c0
Create Date: 2022-09-26 16:12:57.289415

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b6fcd8acd5a'
down_revision = '9328971a22c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('all_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=60), nullable=False),
    sa.Column('phone_number', sa.String(length=12), nullable=True),
    sa.Column('full_name', sa.String(length=100), nullable=True),
    sa.Column('shipping_adress', sa.String(length=200), nullable=True),
    sa.Column('password', sa.String(length=128), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_index(op.f('ix_all_users_role'), 'all_users', ['role'], unique=False)
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('lft', sa.Integer(), nullable=False),
    sa.Column('rgt', sa.Integer(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('tree_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('categories_level_idx', 'categories', ['level'], unique=False)
    op.create_index('categories_lft_idx', 'categories', ['lft'], unique=False)
    op.create_index('categories_rgt_idx', 'categories', ['rgt'], unique=False)
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=True)
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=475), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('photos_path', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('brand_name', sa.String(length=40), nullable=True),
    sa.Column('color', sa.String(length=20), nullable=True),
    sa.Column('gender', sa.String(length=7), nullable=True),
    sa.Column('size', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['category'], ['categories.name'], ),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['all_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=True)
    op.drop_index('ix_user_role', table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('email', sa.VARCHAR(length=60), nullable=False),
    sa.Column('phone_number', sa.VARCHAR(length=12), nullable=True),
    sa.Column('full_name', sa.VARCHAR(length=100), nullable=True),
    sa.Column('shipping_adress', sa.VARCHAR(length=200), nullable=True),
    sa.Column('password', sa.VARCHAR(length=128), nullable=False),
    sa.Column('role', sa.VARCHAR(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_index('ix_user_role', 'user', ['role'], unique=False)
    op.drop_index(op.f('ix_products_name'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_index('categories_rgt_idx', table_name='categories')
    op.drop_index('categories_lft_idx', table_name='categories')
    op.drop_index('categories_level_idx', table_name='categories')
    op.drop_table('categories')
    op.drop_index(op.f('ix_all_users_role'), table_name='all_users')
    op.drop_table('all_users')
    # ### end Alembic commands ###
