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

"""extended whitelist with task name

Revision ID: fc4f164a7b6c
Revises: 8736ad38ca31
Create Date: 2016-11-15 09:09:46.300987

"""

# revision identifiers, used by Alembic.
revision = 'fc4f164a7b6c'
down_revision = '8736ad38ca31'
branch_labels = None
depends_on = None

from alembic import context
from alembic import op
import sqlalchemy as sa


def upgrade():
    table_prefix = context.config.get_main_option('table_prefix')
    op.add_column(
        table_prefix + 'changes_whitelist',
        sa.Column('fuel_task', sa.String, server_default='', nullable=False)
    )


def downgrade():
    table_prefix = context.config.get_main_option('table_prefix')
    op.drop_column(table_prefix + 'changes_whitelist', 'fuel_task')
