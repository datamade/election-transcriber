"""Add server default for image task assignment

Revision ID: 30c6e688863
Revises: 215ce54423be
Create Date: 2016-12-05 11:41:23.795748

"""

# revision identifiers, used by Alembic.
revision = '30c6e688863'
down_revision = '215ce54423be'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.execute('''
        ALTER TABLE image_task_assignment 
        ALTER COLUMN view_count SET DEFAULT 0
    ''')
    op.execute(''' 
        UPDATE image_task_assignment SET
          view_count = 0
        WHERE view_count IS NULL
    ''')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.execute('''
        ALTER TABLE image_task_assignment 
        ALTER COLUMN view_count DROP DEFAULT
    ''')
    op.execute(''' 
        UPDATE image_task_assignment SET
          view_count = NULL
        WHERE view_count = 0
    ''')
    ### end Alembic commands ###