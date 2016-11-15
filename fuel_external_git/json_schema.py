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

gitrepo_single_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GitRepo",
    "description": "Serialized GitRepo object",
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "repo_name": {"type": "string"},
        "env_id": {"type": "number"},
        "git_url": {"type": "string"},
        "ref": {"type": "string"},
        "user_key": {"type": "string"}
    }
}

gitrepo_collection_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GitRepo Collection",
    "description": "Serialized GitRepo collection",
    "type": "object",
    "items": gitrepo_single_schema["properties"]
}

changeswhitelistrule_single_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "ChangesWhitelistRule",
    "description": "Serialized ChangesWhitelistRule object",
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "env_id": {"type": "number"},
        "rule": {"type": "string"},
    }
}

changeswhitelistrule_collection_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "ChangesWhitelistRule Collection",
    "description": "Serialized ChangesWhitelistRule collection",
    "type": "object",
    "items": changeswhitelistrule_single_schema["properties"]
}
