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

"""change_constrains

Revision ID: d59114c46ac4
Revises: e3b840e64e53
Create Date: 2016-08-26 14:33:57.385961

"""

# revision identifiers, used by Alembic.
revision = 'd59114c46ac4'
down_revision = 'e3b840e64e53'
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import context
from alembic import op


def upgrade():
    table_prefix = context.config.get_main_option('table_prefix')
    op.create_unique_constraint('_repo_name_unique',
                                table_prefix + 'repos',
                                ['repo_name'])

    op.alter_column(table_prefix + 'repos',
                    'user_key',
                    type_=sa.UnicodeText(),
                    existing_type=sa.String(255))


def downgrade():
    table_prefix = context.config.get_main_option('table_prefix')
    op.drop_constraint('_repo_name_unique',
                       table_prefix + 'repos')

    op.alter_column(table_prefix + 'repos',
                    'user_key',
                    existing_type=sa.UnicodeText(),
                    type_=sa.String(255))
