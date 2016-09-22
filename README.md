# Nailgun API Extension with External Git Server
### About
Nailgun extension that generates deployment data based on configuration files published in external git repository
### Requirements
Deployed Fuel 9.0 (Mitaka) Master Node

### Installation
Execute following commands on Fuel Master node
```
# yum install git python-pip
# git clone https://github.com/openstack/fuel-nailgun-extension-iac
# cd fuel-nailgun-extension-iac
# pip install -r requirements.txt
# python setup.py install
# nailgun_syncdb
# systemctl restart nailgun.service
```

### How to Use
This extension introduces set of additional Fuel CLI commands which help to associate git repo with particular environment and preform CRUD operations this repo.
```
  gitrepo create
  gitrepo delete
  gitrepo get configs
  gitrepo init
  gitrepo list
  gitrepo update
```
#### Fuel CLI
##### Create association of environment and git repository
```
fuel2 gitrepo create [-h] --env ENV --name NAME --url URL --ref REF
                            [--key KEY]

  --env ENV    ID of environment to configure.
  --name NAME  Name of the git repository. Will be used as directory name for
               repository.
  --url URL    Url of Git repository. User should be specified in this url.
  --ref REF    Git ref. This can be either a branch or Gerrit refspec.
  --key KEY    Path to private key file for accessing repo
```
For example:
```
fuel2 gitrepo create --env 1 --name oscnf1 --url git@github.com:dukov/oscnf.git --ref master --key .ssh/id_rsa
```

##### (Optional) When repo added to environment user may want to initialise new repository with basic settings and tools
```
fuel2 gitrepo init [-h] --repo REPO

  --repo REPO  Repo ID to init
```
For example:
```
fuel2 gitrepo init --repo 11
```
##### (Optional) User can download supported config files from the environment and upload them to configured git repository
```
fuel2 gitrepo get configs [-h] [--env ENV] [--key_path KEY_PATH]
                             [--repo_dir REPO_DIR]

  --env ENV            Env ID
  --key_path KEY_PATH  Path to nodes private key file
  --repo_dir REPO_DIR  Directory to Git repo download
```
For example download configs from all environment and push them to configured repo:
```
fuel2 gitrepo get configs
```
##### Other commands
You can update,delete and list git repo association executing corresponding command
```
fuel2 gitrepo <command>
```
To get more detailed description use:
```
fuel2 help <command>
```
#### Git Repo structure
Here is the example repo structure
```
.
|-- controller_configs
|   `-- glance-api.conf
|-- node_1_configs
|   `-- nova.conf
|-- nova.conf
|-- overrides.yaml
`-- tools
    `-- show-config-for.py
```
There are three levels of configuration: Global, Role, Node. Each level has higher priority in terms of configuration parameters.
* Global - configuration parameters from all configs from this level will be applied to all nodes in environment.
* Role - configuration parameters from all configs from this level will be applied to nodes with particular role. Parameters from this level will override parameters from Global level
* Node - configuration parameters from all configs from this level will be applied to node with particular id. Parameters from this level will override parameters from Global and Role levels

For example we have ```nova.conf``` file with ```debug = True``` in Global level and ```nova.conf``` with ```debug = False```  in Role level. Resulting configuration will be:
```
[DEFAULT]
debug = False
```
Configuration files for Global level should be placed in repo root. Role and Node levels should be described in overrides.yaml placed in repo root directory using following format
```
nodes:
  '<node_id>': '<directory_name>'
roles:
  '<role_name>': '<directory_name>'
```
Example overrides.yaml
```
nodes:
  '1': node_1_configs
  '2': node_2_configs
roles:
  'cinder': 'cinder_configs'
  'compute': 'compute_configs'
  'controller': 'controller_configs'
  'primary-controller': 'controller_configs'
```
Configuration files for Role and Node levels should be placed in corresponding directory described in overrides.yaml


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
