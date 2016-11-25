Team and repository tags
========================

[![Team and repository tags](http://governance.openstack.org/badges/fuel-nailgun-extension-iac.svg)](http://governance.openstack.org/reference/tags/index.html)

<!-- Change things from this point on -->

# Nailgun API Extension with External Git Server
### About
Nailgun extension that generates deployment data based on configuration files published in external
git repository
### Requirements
Operational Fuel 9.x (Mitaka) Master Node

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
Since the 9.<x> version of Fuel extension should be enabled.
To list all available extensions execute following command
```
# fuel2 extension list
```
Than enable extension for a particular environment
```
# fuel2 env extension enable <env_id> -E fuel_external_git
```

### How to Use

This extension introduces two sets of additional Fuel CLI commands. The first set allows the
operator to associate a git repo with a particular environment and preform CRUD operations on
this repo. The second set allows the operator to execute audit and enforce operations on the
environment as well as list the changes made to configuration. It also allows to manage white
lists for these changes.
See details [here](./doc/cli.md).
```
  gitrepo create
  gitrepo delete
  gitrepo get configs
  gitrepo init
  gitrepo list
  gitrepo update

  audit enforce
  audit noop
  audit list outofsync
  audit whitelist show
  audit whitelist add
  audit whitelist delete
```
Create repository and configure nailgun to use it.
```
fuel2 gitrepo create --env 1 --name oscnf1 --url git@github.com:dukov/oscnf.git --ref master \
  --key .ssh/id_rsa
```
Next create repository structure. This can be done manually
(see Repo structure description below) or extension can automatically generate basic structure.
```
fuel2 gitrepo init --repo 11
```
In order to track configuration evolution it is possible to download all configuration files from
the environment into **separate** branch of configured Git repository. User which has been
configured to access repository must have write permissions to it
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
There are three levels of configuration: Global, Role, Node. Each level has higher priority in terms
of configuration parameters.
* Global - configuration parameters from all configs from this level will be applied to all nodes
  in environment.
* Role - configuration parameters from all configs from this level will be applied to nodes with a
  particular role. Parameters from this level will override parameters from Global level
* Node - configuration parameters from all configs from this level will be applied to node with a
  particular id. Parameters from this level will override parameters from Global and Role levels

For example we have ```nova.conf``` file with ```debug = True``` in Global level and ```nova.conf```
with ```debug = False```  in Role level. Resulting configuration will be:
```
[DEFAULT]
debug = False
```
Configuration files for Global level should be placed in repo root. Role and Node levels should be
described in overrides.yaml placed in repo root directory using following format
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
Configuration files for Role and Node levels should be placed in corresponding directory described
in overrides.yaml

### Audit and enforcement
This feature enables the operator to audit the changes made to the environment as well as enforce
configuration.

```
fuel2 audit noop --env <env-id> || --repo <repo-id>
```
Audit is basically a Fuel graph run with noop flag set. This runs the whole graph and records Puppet resources, that would have changed their state. The command above is equivalent to
```
fuel2 env redeploy --noop <env-id>
```

After the audit run, the operator is able to list the changes to the state of Puppet resources on the environment via following command:
```
fuel2 audit list outofsync --task <noop-task-id> || --repo <repo-id>
```
This is a convenient alternative to the stock command:
```
fuel2 task history show <noop-task-id> --include-summary
```

To enforce configuration state, the operator can issue a stock redeploy command:
```
fuel2 env redeploy <env-id>
```

To perform the whole audit-enforce process automatically, this extension provides the following command:
```
fuel2 audit enforce --env <env-id> || --repo <repo-id>
```
This command will run audit, check the changes and will enforce configuration, if needed.

### Audit changes whitelisting
Since fuel-library contains non-idempotent tasks, that contain Puppet resources, which will be
triggered on each deployment run, this extension provides the operator the ability to filter such changes out.

A whitelist rule is a pair of strings. The first one is a fuel task name to match. The second one is what should be included into a Puppet report line for the whitelisted resource change, e.g. for
```
Openstack_tasks::Swift::Proxy_storage/Package[mc]/ensure
```
the whitelist rule could be
```
Package[mc]/ensure
```
A rule with empty fuel_task filter will match to all tasks.

Whitelist rules for an environment can be listed by
```
fuel2 audit whitelist show <env-id>
```
These rules can be managed by following commands:
```
fuel2 audit whitelist add <env-id> --task <fuel-task> --rule <rule>
fuel2 audit whitelist delete <rule-id>
fuel2 audit whitelist load fromfile <env-id> <path-to-yaml>
```

Example YAML file with whitelist rules:
```
- fuel_task: netconfig
  rule: L23_stored_configs
- fuel_task: top-role-compute
  rule: Service[nova-compute]/ensure
```

The default whitelist can be loaded with following command
```
fuel2 audit whitelist load fromfile <env-id> /usr/lib/python2.7/site-packages/fuel_external_git/default_whitelist.yaml
```
Note: this whitelist is not complete as it has been put together on following configuration:
MOS 9.1, Ubuntu, 1 controller, 1 compute+cinder lvm, Neutron GRE.

### REST API
API documentation can be found [here](./doc/api.md)
