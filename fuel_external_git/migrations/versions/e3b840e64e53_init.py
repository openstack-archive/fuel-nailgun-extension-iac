# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

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

from alembic import context
from alembic import op

import sqlalchemy as sa


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
