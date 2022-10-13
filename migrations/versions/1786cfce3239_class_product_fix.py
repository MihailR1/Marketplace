"""class product fix

Revision ID: 1786cfce3239
Revises: f1f19702cf5b
Create Date: 2022-09-28 16:45:34.826380

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1786cfce3239'
down_revision = 'f1f19702cf5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.create_foreign_key(None, 'product', 'user', ['user_id'], ['id'])
    op.drop_column('product', 'category_id')
    op.drop_column('product', 'category_id_number')
    op.drop_column('product', 'category_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('category_name', sa.VARCHAR(length=50), nullable=True))
    op.add_column('product', sa.Column('category_id_number', sa.INTEGER(), nullable=True))
    op.add_column('product', sa.Column('category_id', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.create_foreign_key(None, 'product', 'categories', ['category_id'], ['id'])
    # ### end Alembic commands ###
