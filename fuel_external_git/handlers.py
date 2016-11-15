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

from fuel_external_git import json_schema
from fuel_external_git.objects import ChangesWhitelistRule
from fuel_external_git.objects import ChangesWhitelistRuleCollection
from fuel_external_git.objects import GitRepo
from fuel_external_git.objects import GitRepoCollection

from nailgun.api.v1.handlers.base import BaseHandler
from nailgun.api.v1.handlers.base import CollectionHandler
from nailgun.api.v1.handlers.base import handle_errors
from nailgun.api.v1.handlers.base import serialize
from nailgun.api.v1.handlers.base import SingleHandler
from nailgun.api.v1.handlers.base import validate
from nailgun.api.v1.validators import base
from nailgun import errors
from nailgun import objects


REPOS_DIR = '/var/lib/fuel_repos'


class GitRepoValidator(base.BasicValidator):

    single_schema = json_schema.gitrepo_single_schema
    collection_schema = json_schema.gitrepo_collection_schema

    _blocked_for_update = (
        'env_id',
    )

    @classmethod
    def _validate_master_mgmt(self, data, instance=None):
        d = self.validate_json(data)
        if instance:
            repo_id = instance.id
        else:
            repo_id = d.get('id', None)
        if d.get('manage_master', False):
            for repo in GitRepoCollection.all():
                if repo.manage_master and repo_id != repo.id:
                    raise errors.InvalidData(
                        ("Repo {} already marked for Fuel Master management. "
                         "Disable it first".format(repo.id)),
                        log_message=True)
        return d

    @classmethod
    def validate(self, data):
        return self._validate_master_mgmt(data)

    @classmethod
    def validate_update(self, data, instance):
        d = self._validate_master_mgmt(data, instance)
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


class ChangesWhitelistRuleValidator(base.BasicValidator):

    single_schema = json_schema.changeswhitelistrule_single_schema
    collection_schema = json_schema.changeswhitelistrule_collection_schema

    _blocked_for_update = (
        'env_id',
    )

    @classmethod
    def validate_update(self, data, instance):
        d = self.validate_json(data)
        for k in self._blocked_for_update:
            if k in d and getattr(instance, k) != d[k]:
                raise errors.InvalidData(
                    u"Changing '{0}' for white list is prohibited".format(k),
                    log_message=True
                )

        return d

    # TODO(dnikishov): investigate if there's a more simple way to do this
    @classmethod
    def validate_one_or_multiple(self, data):
        d = self.validate_json(data)
        if not isinstance(d, list):
            d = [d]
        for item in d:
            self.validate_schema(item, self.single_schema)

        return d


class GitRepoCollectionHandler(CollectionHandler):
    collection = GitRepoCollection
    validator = GitRepoValidator


class GitRepoHandler(SingleHandler):
    single = GitRepo
    validator = GitRepoValidator

    @handle_errors
    @validate
    @serialize
    def GET(self, cluster_id, obj_id):
        """:returns: JSONized REST object.

        :http: * 200 (OK)
               * 404 (dashboard entry not found in db)
        """
        self.get_object_or_404(objects.Cluster, cluster_id)

        obj = self.get_object_or_404(self.single, obj_id)
        return self.single.to_json(obj)

    @handle_errors
    @validate
    @serialize
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

    @handle_errors
    @serialize
    def DELETE(self, cluster_id, obj_id):
        """:returns: JSONized REST object.

        :http: * 204 (OK)
               * 404 (object not found in db)
        """
        d_e = self.get_object_or_404(self.single, obj_id)
        self.single.delete(d_e)
        raise self.http(204)


class GitRepoInit(BaseHandler):

    @handle_errors
    @validate
    @serialize
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


class ChangesWhitelistRuleHandler(SingleHandler):
    single = ChangesWhitelistRule
    validator = ChangesWhitelistRuleValidator

    @handle_errors
    @validate
    @serialize
    def GET(self, obj_id):
        """:returns: JSONized REST object.

        :http: * 200 (OK)
               * 404 (dashboard entry not found in db)
        """
        obj = self.get_object_or_404(self.single, obj_id)
        return self.single.to_json(obj)

    @handle_errors
    @validate
    @serialize
    def PUT(self, obj_id):
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

    def PATCH(self, obj_id):
        """:returns: JSONized REST object.

        :http: * 200 (OK)
               * 400 (invalid object data specified)
               * 404 (object not found in db)
        """
        return self.PUT(obj_id)

    @handle_errors
    @serialize
    def DELETE(self, obj_id):
        """:returns: JSONized REST object.

        :http: * 204 (OK)
               * 404 (object not found in db)
        """
        d_e = self.get_object_or_404(self.single, obj_id)
        self.single.delete(d_e)
        raise self.http(204)


class ChangesWhitelistRuleCollectionHandler(CollectionHandler):
    collection = ChangesWhitelistRuleCollection
    validator = ChangesWhitelistRuleValidator

    @handle_errors
    @validate
    @serialize
    def GET(self, env_id):
        """:returns: JSONized REST object.

        :http: * 200 (OK)
               * 404 (dashboard entry not found in db)
        """
        self.get_object_or_404(objects.Cluster, env_id)
        rules = self.collection.get_by_env_id(env_id)
        return self.collection.to_list(rules)

    @handle_errors
    @serialize
    def POST(self, env_id):
        """:returns: JSONized REST object.

        :http: * 201 (object successfully created)
               * 400 (invalid object data specified)
               * 409 (object with such parameters already exists)
        """
        data = self.checked_data(
            validate_method=self.validator.validate_one_or_multiple
        )
        for item in data:
            item['env_id'] = env_id

        new_objs = []
        try:
            for item in data:
                new_objs.append(self.collection.create(item))
        except errors.CannotCreate as exc:
            raise self.http(400, exc.message)

        raise self.http(201, self.collection.to_json(new_objs))
