import os

from nailgun.logger import logger

from nailgun.extensions import BaseExtension
from nailgun.extensions import BasePipeline

from fuel_external_git import handlers
from fuel_external_git.objects import GitRepo
from fuel_external_git import const
from fuel_external_git.openstack_config import OpenStackConfig


class OpenStackConfigPipeline(BasePipeline):
    @classmethod
    def process_deployment(cls, data, cluster, nodes, **kwargs):
        """Genereate OpenStack configuration hash based on configuration files
           stored in git repository associated with a particular environment
           Example of configuration extension:
               configuration:
                 nova_config:
                   DEFAULT/debug:
                     value: True
                   DEFAULT/amqp_durable_queues:
                     value: False
                 keystone_config:
                   DEFAULT/default_publisher_id:
                     ensure: absent
                   DEFAULT/crypt_strength:
                     value: 6000
        """
        repo = GitRepo.get_by_cluster_id(cluster.id)
        GitRepo.checkout(repo)
        repo_path = os.path.join(const.REPOS_DIR, repo.repo_name)

        config_files = [conf for conf in os.listdir(repo_path)
                        if conf.endswith('conf')]

        adv_config = {}
        for conf_file in config_files:
            # TODO(dukov) Config resource name may differ from file name
            config = OpenStackConfig(os.path.join(repo_path, conf_file),
                                     conf_file)
            adv_config[config.config_name] = config.to_config_dict()
        if adv_config != {}:
            for node_config in data:
                node_config['configuration'] = adv_config
        logger.info(adv_config)
        return data


class ExternalGit(BaseExtension):
    name = 'fuel_external_git'
    version = '1.0.0'
    description = 'Nailgun extension which uses git repo for config files'

    urls = [{'uri': r'/clusters/git-repos/?$',
             'handler': handlers.GitRepoCollectionHandler},
            {'uri':
                r'/clusters/(?P<cluster_id>\d+)/git-repos/(?P<obj_id>\d+)?$',
             'handler': handlers.GitRepoHandler}]

    data_pipelines = [
        OpenStackConfigPipeline,
    ]

    @classmethod
    def alembic_migrations_path(cls):
        return os.path.join(os.path.dirname(__file__), 'migrations')
