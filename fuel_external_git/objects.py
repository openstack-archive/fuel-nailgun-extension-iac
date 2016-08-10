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
        repo_path = os.path.join(const.REPOS_DIR, data['repo_name'])
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        repo = Repo.clone_from(data['git_url'], repo_path)
        instance = super(GitRepo, self).create(data)
        instance.repo = repo
        return instance

    @classmethod
    def checkout(self, instance):
        commit = instance.repo.remotes.origin.fetch(refspec=instance.ref)[0].commit
        instance.repo.head.reference = commit
        
    def remove_repo(self):
        pass

class GitRepoCollection(NailgunCollection):
    single = GitRepo

