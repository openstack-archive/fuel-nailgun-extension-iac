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

import copy
import os
import yaml

from fuel_external_git import const
from fuel_external_git import handlers
from fuel_external_git.objects import GitRepo
from fuel_external_git.settings import GitExtensionSettings
from fuel_external_git import utils

from nailgun.extensions import BaseExtension
from nailgun.extensions import BasePipeline
from nailgun.logger import logger


class OpenStackConfigPipeline(BasePipeline):
    # TODO(dukov) add cluster remove callback

    @classmethod
    def lcm_v1(cls, node, node_data):
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

        common = copy.deepcopy(global_config)
        roles = node_data['roles']
        uid = node_data['uid']
        logger.debug("Node {0} roles {1}".format(uid, roles))
        for role in roles:
            utils.deep_merge(common,
                             override_configs['roles'].get(role, {}))

        logger.debug("Config Node {0} with roles {1}".format(uid, common))

        utils.deep_merge(common,
                         override_configs['nodes'].get(uid, {}))
        return {'configuration': common}

    @classmethod
    def process_deployment_for_node(cls, node, node_data):
        """Updating deployment info

           Genereate OpenStack configuration hash based on configuration files
           stored in git repository associated with a particular environment
        """
        logger.info("Started serialisation for node {}".format(node.id))
        repo = GitRepo.get_by_cluster_id(node.cluster_id)
        if not repo:
            return node_data

        GitRepo.checkout(repo)
        repo_path = os.path.join(const.REPOS_DIR, repo.repo_name)

        data = self.lcm_v1(node, node_data)
        utils.deep_merge(node_data, data)
        logger.debug("Node {0} config from git {1}".format(uid, common))
        logger.info("Finished serialisation for node {}".format(node.id))
        return node_data

    @classmethod
    def process_deployment_for_cluster(self, cluster, data):
        logger.info("Started serialisation for cluster {}".format(cluster.id))
        repo = GitRepo.get_by_cluster_id(cluster.id)
        if not repo:
            return data

        if repo.manage_master:
            GitRepo.checkout(repo)
            repo_path = os.path.join(const.REPOS_DIR, repo.repo_name)
            resource_mapping = ExternalGit.ext_settings['master_mapping']
            master_config = utils.get_config_hash(
                repo_path,
                {'master_config': resource_mapping.get('master_config', {})},
                exts=['yaml']
            )

            data['master_config'] = master_config

        logger.info("Finished serialisation for cluster {}".format(cluster.id))
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
