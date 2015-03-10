"""Adding status

Revision ID: 47a39bab0bc4
Revises: 1b6cbddb3fd5
Create Date: 2015-03-09 16:41:05.883645

"""

# revision identifiers, used by Alembic.
revision = '47a39bab0bc4'
down_revision = '1b6cbddb3fd5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('e609eca62d18_columbia')
    op.add_column('form_field', sa.Column('status', sa.String(), nullable=True))
    op.add_column('form_meta', sa.Column('status', sa.String(), nullable=True))
    op.add_column('form_section', sa.Column('status', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('form_section', 'status')
    op.drop_column('form_meta', 'status')
    op.drop_column('form_field', 'status')
    op.create_table('e609eca62d18_columbia',
    sa.Column('date_added', postgresql.TIMESTAMP(timezone=True), server_default=sa.text(u'now()'), autoincrement=False, nullable=True),
    sa.Column('transcriber', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('image_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('nulos', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('nulos_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('nulos_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('juan_manuel_santos_calderon', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('juan_manuel_santos_calderon_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('juan_manuel_santos_calderon_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('puesto', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('puesto_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('puesto_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('mesa', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('mesa_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('mesa_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('municipality', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('municipality_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('municipality_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('municipality_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('municipality_id_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('municipality_id_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('lugar', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('lugar_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('lugar_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('zone', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('zone_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('zone_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('department_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('department_name_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('department_name_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('department_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('department_id_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('department_id_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('total', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('total_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('total_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('no_marks', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('no_marks_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('no_marks_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('blanks', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('blanks_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('blanks_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('oscar_ivan_zuluaga', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('oscar_ivan_zuluaga_blank', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('oscar_ivan_zuluaga_not_legible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=u'e609eca62d18_columbia_pkey')
    )
    ### end Alembic commands ###