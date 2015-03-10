"""Adding FormMeta index

Revision ID: 36e20e3215bd
Revises: 513666e6ea0b
Create Date: 2015-03-10 16:53:15.346322

"""

# revision identifiers, used by Alembic.
revision = '36e20e3215bd'
down_revision = '513666e6ea0b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('form_meta', sa.Column('index', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('form_meta', 'index')
    ### end Alembic commands ###
