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
