import json
import os
import web

from nailgun.api.v1.handlers.base import SingleHandler, CollectionHandler
from nailgun.api.v1.handlers.base import content
from nailgun.logger import logger
from nailgun import objects

from fuel_external_git.objects import GitRepo, GitRepoCollection 
from git import Repo

REPOS_DIR = '/var/lib/fuel_repos'

class GitRepoCollectionHandler(CollectionHandler):
    collection = GitRepoCollection

class GitRepoHandler(SingleHandler):
    single = GitRepo

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

