"""empty message

Revision ID: 322be74fee7c
Revises: c10e72700bec
Create Date: 2022-07-10 01:43:59.817013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '322be74fee7c'
down_revision = 'c10e72700bec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('log_request', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'log_request', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'log_request', type_='foreignkey')
    op.drop_column('log_request', 'user_id')
    # ### end Alembic commands ###