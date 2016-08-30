from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UnicodeText

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
