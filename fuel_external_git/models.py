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

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UnicodeText
from sqlalchemy import Boolean

from nailgun.db.sqlalchemy.models.base import Base


class GitRepo(Base):
    __tablename__ = 'fuel_external_git_repos'
    id = Column(Integer, primary_key=True)
    repo_name = Column(UnicodeText, nullable=False)
    env_id = Column(Integer, unique=True, nullable=False)
    git_url = Column(String(255), default='', server_default='',
                     nullable=False)
    ref = Column(String(255), default='', server_default='', nullable=False)
    user_key = Column(String(255), default='', server_default='',
                      nullable=False)
    manage_master = Column(Boolean(), nullable=False)
