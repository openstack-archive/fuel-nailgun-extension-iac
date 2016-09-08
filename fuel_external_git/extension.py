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

import os
import copy
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
    # TODO(dukov) add cluster remove callback
    @classmethod
    def process_deployment(cls, data, cluster, nodes, **kwargs):
        """Updating deployment info

           Genereate OpenStack configuration hash based on configuration files
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
        if not repo:
            return data
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
            overrides = {'roles': {}, 'nodes': {}}

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

        logger.debug("Override configs {}".format(override_configs))

        for node_config in data:
            common = copy.deepcopy(global_config)
            roles = node_config['roles']
            uid = node_config['uid']
            logger.debug("Node {0} roles {1}".format(uid, roles))
            for role in roles:
                utils.deep_merge(common,
                                 override_configs['roles'].get(role, {}))

            logger.debug("Config Node {0} with roles {1}".format(uid, common))

            utils.deep_merge(common,
                             override_configs['nodes'].get(uid, {}))

            node_config['configuration'] = common
            logger.info("Node {0} config from git {1}".format(uid, common))
        return data

# TODO(dukov) Remove decorator extension management is available
@utils.register_extension(u'fuel_external_git')
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
