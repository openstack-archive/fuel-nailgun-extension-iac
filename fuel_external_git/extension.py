import os
import logging

from nailgun import objects
from nailgun.logger import logger

from nailgun.extensions import BaseExtension
from nailgun.extensions import BasePipeline

from fuel_external_git import handlers


class OpenStackConfigPipeline(BasePipeline):
    pass

class ExternalGit(BaseExtension):
    name = 'fuel_external_git'
    version = '1.0.0'
    description = 'Nailgun extension which uses git repo for config files'

    urls = [{'uri': r'/clusters/git-repos/?$',
             'handler': handlers.GitRepoCollectionHandler},
            {'uri': r'/clusters/(?P<cluster_id>\d+)/git-repos/(?P<obj_id>\d+)?$',
             'handler': handlers.GitRepoHandler}]

    data_pipelines = [
        OpenStackConfigPipeline,
    ]

    @classmethod
    def alembic_migrations_path(cls):
        return os.path.join(os.path.dirname(__file__), 'migrations')
