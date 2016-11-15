### API
Extension supports following REST API calls
#### GET /clusters/git-repos
Returns list of configured git repos for all clusters/environments
Example
```
curl -H "X-Auth-Token: $(fuel token)" http://localhost:8000/api/v1/clusters/git-repos
```

#### POST /clusters/git-repos
Create new repo for particular cluster
Input data schema:
```
"$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Cluster",
    "description": "Serialized GitRepo object",
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "repo_name": {"type": "string"},
        "env_id": {"type": "number"},
        "git_url": {"type": "string"},
        "ref": {"type": "string"},
        "user_key": {"type": "string"}
```

Example
```
curl -X POST -H "X-Auth-Token: $(fuel token)" http://localhost:8000/api/v1/clusters/git-repos -d '{"user_key": "", "git_url": "https://github.com/dukov/openstack-configs", "env_id": 5, "ref": "master", "repo_name": "osconf1"}'
```

#### PUT /clusters/(cluster_id)/git-repos/(obj_id)
Updates repo with obj_id info for cluster cluster_id
Example:
```
curl -X PUT -H 'X-Auth-Token: $(fuel token)' http://localhost:8000/api/v1/clusters/4/git-repos/2 -d '{"ref": "master"}'
```


#### GET /clusters/changes-whitelist/(obj_id)
Returns the serialized whitelist rule object
Example
```
curl -H "X-Auth-Token: $(fuel token)" http://localhost:8000/api/v1/clusters/changes-whitelist/1
```

#### PUT /clusters/changes-whitelist/(obj_id)
Updates a whitelist rule
Input data schema:
```
"$schema": "http://json-schema.org/draft-04/schema#",
"title": "ChangesWhitelistRule",
"description": "Serialized ChangesWhitelistRule object",
"type": "object",
"properties": {
    "rule": {"type": "string"},
}
```
Example
```
curl -H "X-Auth-Token: $(fuel token)" -X PUT http://localhost:8000/api/v1/clusters/changes-whitelist/1 -d '{"rule": "new-rule-string"}'
```

#### DELETE /clusters/changes-whitelist/(obj_id)
Deletes a whitelist rule
Example
```
curl -H "X-Auth-Token: $(fuel token)" -X DELETE http://localhost:8000/api/v1/clusters/changes-whitelist/1
```

#### GET /clusters/(env_id)/changes-whitelist/
Returns the whitelist rules for a specified environment
Example
```
curl -H "X-Auth-Token: $(fuel token)" http://localhost:8000/api/v1/clusters/1/changes-whitelist/
```
#### POST /clusters/(env_id)/changes-whitelist/
Creates one or more whitelist rule(s)
Input data schema:
```
"$schema": "http://json-schema.org/draft-04/schema#",
"title": "ChangesWhitelistRule Collection",
"description": "Serialized ChangesWhitelistRule collection",
"type": "object",
"items": {
    "rule": {"type": "string"}
}
```
Example
```
curl -H "X-Auth-Token: $(fuel token)" -X POST http://localhost:8000/api/v1/clusters/1/changes-whitelist/ -d '[{"rule": "new-rule-string"}, {"rule": "new-rule-2"}]'
```
