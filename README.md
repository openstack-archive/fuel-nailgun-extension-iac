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
Next extension should be enabled. To list all available extensions execute following command
```
# fuel2 extension list 
```
Than enable extension for a particular environment
```
# fuel2 env extension enable <env_id> -E fuel_external_git
```

### How to Use

This extension introduces set of additional Fuel CLI commands which help to associate git repo with particular environment and preform CRUD operations this repo. See details [here](../blob/master/doc/cli.md).
```
  gitrepo create
  gitrepo delete
  gitrepo get configs
  gitrepo init
  gitrepo list
  gitrepo update
```
First you need to create repository and configure nailgun to use it.
```
fuel2 gitrepo create --env 1 --name oscnf1 --url git@github.com:dukov/oscnf.git --ref master --key .ssh/id_rsa
```
Next you need to create repository structure. You can do this manually (see Repo structure description below) or extension can automatically generate basic structure for you. 
```
fuel2 gitrepo init --repo 11
```
In order to track configuration evolution it is possible to download all configuration files from the environment into **separate** branch of configured Git repository. User configured to access repository must have write permissions to it
```
fuel2 gitrepo get configs --env 1
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

### REST API
API documentation can be found [here](../blob/master/doc/api.md) 
