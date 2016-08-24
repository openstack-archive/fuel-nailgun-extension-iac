from nailgun import objects
from nailgun.errors import errors
from nailgun.api.v1.validators import base
from nailgun.api.v1.handlers.base import content
from nailgun.api.v1.handlers.base import \
        SingleHandler, CollectionHandler, BaseHandler

from fuel_external_git.objects import GitRepo, GitRepoCollection
from fuel_external_git import json_schema

REPOS_DIR = '/var/lib/fuel_repos'


class GitRepoValidator(base.BasicValidator):

    single_schema = json_schema.single_schema
    collection_schema = json_schema.collection_schema

    _blocked_for_update = (
        'env_id',
    )

    @classmethod
    def validate_update(self, data, instance):
        d = self.validate_json(data)
        env_id = d.get('env_id')
        if env_id:
            cluster = objects.Cluster.get_by_uid(env_id)
            if not cluster:
                raise errors.InvalidData(
                    "Invalid cluster ID", log_message=True)

        for k in self._blocked_for_update:
            if k in d and getattr(instance, k) != d[k]:
                raise errors.InvalidData(
                    u"Changing '{0}' for git repo is prohibited".format(k),
                    log_message=True
                )

        return d


class GitRepoCollectionHandler(CollectionHandler):
    collection = GitRepoCollection
    validator = GitRepoValidator


class GitRepoHandler(SingleHandler):
    single = GitRepo
    validator = GitRepoValidator

    def GET(self, cluster_id, obj_id):
        """:returns: JSONized REST object.

        :http: * 200 (OK)
               * 404 (dashboard entry not found in db)
        """
        self.get_object_or_404(objects.Cluster, cluster_id)

        obj = self.get_object_or_404(self.single, obj_id)
        return self.single.to_json(obj)

    @content
    def PUT(self, cluster_id, obj_id):
        """:returns: JSONized REST object.

        :http: * 200 (OK)
               * 400 (invalid object data specified)
               * 404 (object not found in db)
        """
        obj = self.get_object_or_404(self.single, obj_id)

        data = self.checked_data(
            self.validator.validate_update,
            instance=obj
        )
        self.single.update(obj, data)
        return self.single.to_json(obj)

    def PATCH(self, cluster_id, obj_id):
        """:returns: JSONized REST object.

        :http: * 200 (OK)
               * 400 (invalid object data specified)
               * 404 (object not found in db)
        """
        return self.PUT(cluster_id, obj_id)

    @content
    def DELETE(self, cluster_id, obj_id):
        """:returns: JSONized REST object.

        :http: * 204 (OK)
               * 404 (object not found in db)
        """
        d_e = self.get_object_or_404(self.single, obj_id)
        self.single.delete(d_e)
        raise self.http(204)


class GitRepoInit(BaseHandler):

    @content
    def PUT(self, env_id, obj_id):
        """:returns: JSONized REST object.

        :http: * 200 (OK)
               * 400 (invalid object data specified)
               * 404 (object not found in db)
        """
        obj = self.get_object_or_404(GitRepo, obj_id)
        obj = GitRepo.get_by_cluster_id(obj.env_id)
        GitRepo.init(obj)
        raise self.http(200, "{}")
