import os
import yaml

from nailgun.logger import logger

from nailgun.extensions import BaseExtension
from nailgun.extensions import BasePipeline

from fuel_external_git import handlers
from fuel_external_git.objects import GitRepo
from fuel_external_git.settings import GitExtensionSettings
from fuel_external_git import const
from fuel_external_git import utils


class OpenStackConfigPipeline(BasePipeline):
    # TODO (dukov) add cluster remove callback
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
        resource_mapping = ExternalGit.ext_settings['resource_mapping']
        exts_list = utils.get_file_exts_list(resource_mapping)

        global_config = utils.get_config_hash(repo_path,
                                              resource_mapping,
                                              exts=exts_list)

        # Read config for overrides
        # Overrides file should contain following mapping
        #  - role:config_file_dir
        #  - node_id:config_file_dir
        # Config options from files for roles should override global
        # configs (placed in repo root).
        # Config options from files for nodes should override global
        # and roles config oprions
        overrides_file = os.path.join(repo_path, 'overrides.yaml')
        if os.path.exists(overrides_file):
            overrides = yaml.load(open(overrides_file))
        else:
            overrides = {}

        override_configs = {}
        # ent = roles|nodes
        for ent, override in overrides.items():
            override_configs[ent] = {}
            # key = role_name|node_id
            for key, path in override.items():
                file_dir = os.path.join(repo_path, path)
                config_hash = utils.get_config_hash(file_dir,
                                                    resource_mapping,
                                                    exts=exts_list)
                override_configs[ent][key] = config_hash

        for node_config in data:
            roles = node_config['roles']
            uid = node_config['uid']
            for role in roles:
                utils.deep_merge(global_config,
                                 override_configs['roles'].get(role, {}))

            utils.deep_merge(global_config,
                             override_configs['nodes'].get(uid, {}))

            node_config['configuration'] = global_config
            logger.info("Node config from git {}".format(global_config))
        return data


class ExternalGit(BaseExtension):
    name = 'fuel_external_git'
    version = '1.0.0'
    description = 'Nailgun extension which uses git repo for config files'

    urls = [{'uri': r'/clusters/git-repos/?$',
             'handler': handlers.GitRepoCollectionHandler},
            {'uri':
                r'/clusters/(?P<cluster_id>\d+)/git-repos/(?P<obj_id>\d+)?$',
             'handler': handlers.GitRepoHandler},
            {'uri':
                r'/clusters/(?P<env_id>\d+)/git-repos/(?P<obj_id>\d+)/init?$',
             'handler': handlers.GitRepoInit}]

    data_pipelines = [
        OpenStackConfigPipeline,
    ]

    ext_settings = GitExtensionSettings().config

    @classmethod
    def alembic_migrations_path(cls):
        return os.path.join(os.path.dirname(__file__), 'migrations')
