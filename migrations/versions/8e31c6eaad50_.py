"""empty message

Revision ID: 8e31c6eaad50
Revises: 98bca71f058a
Create Date: 2022-07-10 19:53:23.326558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e31c6eaad50'
down_revision = '98bca71f058a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('log_request', sa.Column('imgur_link', sa.String(length=1024), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('log_request', 'imgur_link')
    # ### end Alembic commands ###
