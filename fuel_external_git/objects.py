import os
import shutil
from nailgun.db import db
from nailgun.objects import NailgunObject, NailgunCollection
from nailgun.objects.serializers.base import BasicSerializer

from git import Repo
from git import exc

from fuel_external_git.models import GitRepo
from fuel_external_git import const

class GitRepoSerializer(BasicSerializer):
    fields = (
        "id",
        "repo_name",
        "env_id",
        "git_url",
        "ref",
        "user_key"
    )

class GitRepo(NailgunObject):
    model = GitRepo
    serializer = GitRepoSerializer

    @classmethod
    def get_by_cluster_id(self, cluster_id):
        instance = db().query(self.model).\
                              filter(self.model.env_id == cluster_id).\
                              first()
        if instance is not None:
            try:
                instance.repo = Repo(os.path.join(const.REPOS_DIR, instance.repo_name))
            except exc.NoSuchPathError:
                # TODO(dukov) Put some logging here
                instance.repo = GitRepo.clone(instance.git_url)
        return instance

    @classmethod
    def create(self, data):
        if not os.path.exists(const.REPOS_DIR):
            os.mkdir(const.REPOS_DIR)
        repo_path = os.path.join(const.REPOS_DIR, data['repo_name'])
        if os.path.exists(repo_path):
            # TODO(dukov) add some logging here
            shutil.rmtree(repo_path)

        self._create_key_file(data['repo_name'], data['key'])
        os.environ['GIT_SSH_COMMAND'] = self._get_ssh_cmd(data['repo_name'])
        repo = Repo.clone_from(data['git_url'], repo_path)

        instance = super(GitRepo, self).create(data)
        instance.repo = repo
        return instance

    @classmethod
    def checkout(self, instance):
        ssh_cmd = self._get_ssh_cmd(instance.repo_name)

        if not os.path.exists(self._get_key_path(instance.repo_name)):
            # TODO(dukov) put some logging here
            self._create_key_file(instance.repo_name)

        with instance.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
            commit = instance.repo.remotes.origin.fetch(refspec=instance.ref)[0].commit
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
        return 'ssh -o StrictHostKeyChecking=no -i ' + key_path

class GitRepoCollection(NailgunCollection):
    single = GitRepo

