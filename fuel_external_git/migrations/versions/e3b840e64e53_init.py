"""Init

Revision ID: e3b840e64e53
Revises:
Create Date: 2016-08-09 16:59:36.504052

"""

# revision identifiers, used by Alembic.
revision = 'e3b840e64e53'
down_revision = None
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import context
from alembic import op
from sqlalchemy.dialects import postgresql as psql


def upgrade():
    table_prefix = context.config.get_main_option('table_prefix')
    op.create_table(
        table_prefix + 'repos',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('repo_name', sa.Unicode(100), nullable=False),
        sa.Column('env_id', sa.Integer(), nullable=False),
        sa.Column('git_url', sa.String(255),
                  server_default='', nullable=False),
        sa.Column('ref', sa.String(255),
                  server_default='', nullable=False),
        sa.Column('user_key', sa.String(255),
                  server_default='', nullable=False),
        sa.UniqueConstraint('env_id', name='_env_id_unique'))


def downgrade():
    table_prefix = context.config.get_main_option('table_prefix')
    op.drop_table(table_prefix + 'repos')
