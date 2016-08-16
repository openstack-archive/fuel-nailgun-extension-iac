# Nailgun API Extension with External Git Server
### About
Nailgun extension that generates deployment data based on configuration files published in external git repository
### Requirements
Deployed Fuel 9.0 (Mitaka) Master Node

### Installation
Execute following commands on Fuel Master node
```
# yum install git python-pip
# git clone https://github.com/dukov/fuel-external-git
# cd fuel-external-git
# pip install -r requirements.txt
# python setup.py install
# nailgun_syncdb
# service nailgun reload
```

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
    "description": "Serialized Cluster object",
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

#### PUT /clusters/(?P<cluster_id>\d+)/git-repos/(?P<obj_id>\d+)
Updates repo with obj_id info for cluster cluster_id
Example:
```
curl -X PUT -H 'X-Auth-Token: $(fuel token)' http://localhost:8000/api/v1/clusters/4/git-repos/2 -d '{"ref": "master"}'
```
