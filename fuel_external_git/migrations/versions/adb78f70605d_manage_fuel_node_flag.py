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

"""Manage fuel node flag

Revision ID: adb78f70605d
Revises: d59114c46ac4
Create Date: 2016-09-26 10:10:37.779555

"""

# revision identifiers, used by Alembic.
revision = 'adb78f70605d'
down_revision = 'd59114c46ac4'
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import context
from alembic import op


def upgrade():
    table_prefix = context.config.get_main_option('table_prefix')
    op.add_column(
        table_prefix + 'repos',
        sa.Column('manage_master', sa.Boolean(), nullable=True)
    )


def downgrade():
    table_prefix = context.config.get_main_option('table_prefix')
    op.drop_column(table_prefix + 'repos', 'manage_master')
