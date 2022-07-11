"""empty message

Revision ID: 98bca71f058a
Revises: c4ab0518747c
Create Date: 2022-07-10 18:16:20.823167

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98bca71f058a'
down_revision = 'c4ab0518747c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('upload_to_imgur', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'upload_to_imgur')
    # ### end Alembic commands ###
