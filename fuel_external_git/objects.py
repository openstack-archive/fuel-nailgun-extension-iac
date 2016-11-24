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
import shutil
import time

from fuel_external_git import const
from fuel_external_git.models import ChangesWhitelistRule
from fuel_external_git.models import GitRepo

from git import exc
from git import Repo

from nailgun.consts import CLUSTER_STATUSES
from nailgun.db import db
from nailgun.logger import logger
from nailgun.objects import Cluster
from nailgun.objects import NailgunCollection
from nailgun.objects import NailgunObject
from nailgun.objects.serializers.base import BasicSerializer


class GitRepoSerializer(BasicSerializer):
    fields = (
        "id",
        "repo_name",
        "env_id",
        "git_url",
        "ref",
        "user_key",
        "manage_master"
    )


class ChangesWhitelistRuleSerializer(BasicSerializer):
    fields = (
        "id",
        "env_id",
        "rule",
        "fuel_task"
    )


class GitRepo(NailgunObject):
    model = GitRepo
    serializer = GitRepoSerializer

    @classmethod
    def get_by_cluster_id(self, cluster_id):
        instance = db().query(self.model).\
            filter(self.model.env_id == cluster_id).first()
        if instance is not None:
            try:
                instance.repo = Repo(os.path.join(const.REPOS_DIR,
                                                  instance.repo_name))
            except exc.NoSuchPathError:
                logger.debug("Repo folder does not exist. Cloning repo")
                self._create_key_file(instance.repo_name, instance.user_key)
                if instance.user_key:
                    os.environ['GIT_SSH'] = \
                        self._get_ssh_cmd(instance.repo_name)

                repo_path = os.path.join(const.REPOS_DIR, instance.repo_name)
                repo = Repo.clone_from(instance.git_url, repo_path)
                instance.repo = repo
        return instance

    @classmethod
    def create(self, data):
        if not os.path.exists(const.REPOS_DIR):
            os.mkdir(const.REPOS_DIR)
        repo_path = os.path.join(const.REPOS_DIR, data['repo_name'])
        if os.path.exists(repo_path):
            logger.debug('Repo directory exists. Removing...')
            shutil.rmtree(repo_path)

        user_key = data.get('user_key', '')
        if user_key:
            self._create_key_file(data['repo_name'], user_key)
            os.environ['GIT_SSH'] = self._get_ssh_cmd(data['repo_name'])
        repo = Repo.clone_from(data['git_url'], repo_path)

        instance = super(GitRepo, self).create(data)
        instance.repo = repo
        return instance

    @classmethod
    def update(self, instance, data):
        super(GitRepo, self).update(instance, data)
        if 'user_key' in data:
            instance = GitRepo.get_by_cluster_id(instance.env_id)
            self._create_key_file(instance.repo_name, instance.user_key)

    @classmethod
    def checkout(self, instance):
        fetch_file = os.path.join(
            const.REPOS_DIR,
            instance.repo_name,
            '.git/FETCH_HEAD'
        )
        if os.path.exists(fetch_file):
            current_ts = time.time()
            cluster = Cluster.get_by_uid(instance.env_id)
            last_fetch = os.stat(fetch_file).st_mtime
            if cluster.status != CLUSTER_STATUSES.deployment and \
                current_ts - last_fetch < const.REPO_TTL:
                return

        logger.debug("Repo TTL exceeded. Fetching code...")
        git_shell_env = {}
        if instance.user_key:
            ssh_cmd = self._get_ssh_cmd(instance.repo_name)

            if not os.path.exists(self._get_key_path(instance.repo_name)):
                logger.debug('Key file does not exist. Creating...')
                self._create_key_file(instance.repo_name)

            logger.debug("Updating ENV with ssh command")
            git_shell_env['GIT_SSH'] = ssh_cmd

        with instance.repo.git.custom_environment(**git_shell_env):
            commit = instance.repo.remotes.origin.fetch(refspec=instance.ref)
            commit = commit[0].commit
            instance.repo.head.reference = commit
            instance.repo.head.reset(index=True, working_tree=True)

    @classmethod
    def _create_key_file(self, repo_name, data):
        key_path = self._get_key_path(repo_name)
        with open(key_path, 'w') as key_file:
            key_file.write(data)
        os.chmod(key_path, 0o600)

    @classmethod
    def _get_key_path(self, repo_name):
        return os.path.join(const.REPOS_DIR, repo_name + '.key')

    @classmethod
    def _get_ssh_cmd(self, repo_name):
        key_path = self._get_key_path(repo_name)
        git_ssh_file = os.path.join(const.REPOS_DIR, repo_name + '.sh')
        with open(git_ssh_file, 'w') as ssh_wrap:
            ssh_wrap.write("#!/bin/bash\n")
            ssh_wrap.write((
                "exec /usr/bin/ssh "
                "-o UserKnownHostsFile=/dev/null "
                "-o StrictHostKeyChecking=no "
                "-i {0} \"$@\"".format(key_path)
            ))
        os.chmod(git_ssh_file, 0o755)
        return git_ssh_file


class GitRepoCollection(NailgunCollection):
    single = GitRepo


class ChangesWhitelistRule(NailgunObject):
    model = ChangesWhitelistRule
    serializer = ChangesWhitelistRuleSerializer


class ChangesWhitelistRuleCollection(NailgunCollection):
    single = ChangesWhitelistRule

    @classmethod
    def get_by_env_id(self, env_id):
        whitelist = filter(lambda r: r.env_id == env_id,
                           ChangesWhitelistRuleCollection.all())
        return whitelist
