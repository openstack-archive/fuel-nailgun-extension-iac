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

from __future__ import absolute_import

import fabric.api
import logging
import os
import time

from cliff import command
from cliff import lister
from git import Repo

from fuelclient import client
if hasattr(client, 'DefaultAPIClient'):
    # Handling python-fuelclient version >= 10.0
    fc_client = client.DefaultAPIClient
else:
    # Handling python-fuelclient version <= 9.0
    fc_client = client.APIClient
from fuelclient.common import data_utils
from fuelclient.objects import Environment
from fuelclient.objects import Task

import fuel_external_git.audit as audit
from fuel_external_git.const import AUDIT_TASK_CHECK_INTERVAL
from fuel_external_git.settings import GitExtensionSettings


LOG = logging.getLogger(__name__)


class GitRepoList(lister.Lister, command.Command):
    columns = (
        'id',
        'repo_name',
        'env_id',
        'git_url',
        'ref',
        'manage_master',
    )

    def get_parser(self, prog_name):
        parser = super(GitRepoList, self).get_parser(prog_name)
        parser.add_argument('--env', type=int, help='Env ID', required=False)
        return parser

    def take_action(self, parsed_args):
        data = fc_client.get_request('/clusters/git-repos/')
        if parsed_args.env:
            data = [entry for entry in data
                    if entry['env_id'] == parsed_args.env]
        data = data_utils.get_display_data_multi(self.columns, data)
        return (self.columns, data)


class AddRepo(command.Command):
    columns = (
        'id',
        'repo_name',
        'env_id',
        'git_url',
        'ref',
        'manage_master',
    )

    def get_parser(self, prog_name):
        parser = super(AddRepo, self).get_parser(prog_name)
        mm = parser.add_mutually_exclusive_group(required=False)
        parser.add_argument('--env',
                            type=int,
                            help='ID of environment to configure.',
                            required=True)

        parser.add_argument('--name',
                            type=str,
                            help=('Name of the git repository. '
                                  'Will be used as directory '
                                  'name for repository.'),
                            required=True)

        parser.add_argument('--url',
                            type=str,
                            help=('Url of Git repository. '
                                  'User should be specified in this url.'),
                            required=True)

        parser.add_argument('--ref',
                            type=str,
                            help=('Git ref. This can be either a branch '
                                  'or Gerrit refspec.'),
                            required=True)

        parser.add_argument('--key',
                            type=str,
                            help='Path to private key file for accessing repo',
                            required=False)

        mm.add_argument('--manage-master',
                        dest='manage_master',
                        help='Enable Fuel master management from this repo',
                        action='store_true',
                        required=False)

        mm.add_argument('--no-manage-master',
                        dest='manage_master',
                        help='Disable Fuel master management from this repo',
                        action='store_false',
                        required=False)
        parser.set_defaults(manage_master=False)
        return parser

    def take_action(self, parsed_args):
        data = {
            'repo_name': parsed_args.name,
            'env_id': parsed_args.env,
            'git_url': parsed_args.url,
            'ref': parsed_args.ref,
            'manage_master': parsed_args.manage_master,
        }

        if parsed_args.key:
            with open(parsed_args.key) as key_file:
                data['user_key'] = key_file.read()

        fc_client.post_request('/clusters/git-repos/', data)
        return (self.columns, data)


class DeleteRepo(command.Command):
    columns = (
        'id'
    )

    def get_parser(self, prog_name):
        parser = super(DeleteRepo, self).get_parser(prog_name)
        parser.add_argument('--repo',
                            type=int,
                            help='Repo ID to delete',
                            required=True)

        parser.add_argument('--env',
                            type=int,
                            help='Environment to delete Git repo object from',
                            required=False)
        return parser

    def take_action(self, parsed_args):
        repo_id = parsed_args.repo
        if parsed_args.env:
            env = parsed_args.env
        else:
            repos = fc_client.get_request('/clusters/git-repos/')
            env = [repo['env_id'] for repo in repos
                   if repo['id'] == parsed_args.repo][0]

        del_path = "/clusters/{0}/git-repos/{1}"
        fc_client.delete_request(del_path.format(env, repo_id))
        return (self.columns, {})


class UpdateRepo(command.Command):
    columns = (
        'id',
        'repo_name',
        'git_url',
        'ref',
        'manage_master',
    )

    def get_parser(self, prog_name):
        parser = super(UpdateRepo, self).get_parser(prog_name)
        mm = parser.add_mutually_exclusive_group(required=False)
        parser.add_argument('--repo',
                            type=int,
                            help='Repo ID to update',
                            required=True)

        parser.add_argument('--name',
                            type=str,
                            help=('Name of the git repository. '
                                  'Will be used as directory '
                                  'name for repository.'),
                            required=False)

        parser.add_argument('--url',
                            type=str,
                            help=('Url of Git repository. '
                                  'User should be specified in this url.'),
                            required=False)

        parser.add_argument('--ref',
                            type=str,
                            help=('Git ref. This can be either a branch '
                                  'or Gerrit refspec.'),
                            required=False)

        parser.add_argument('--key',
                            type=str,
                            help='Path to private key file for accessing repo',
                            required=False)

        mm.add_argument('--manage-master',
                        dest='manage_master',
                        help='Enable Fuel master management from this repo',
                        action='store_true',
                        required=False)

        mm.add_argument('--no-manage-master',
                        dest='manage_master',
                        help='Disable Fuel master management from this repo',
                        action='store_false',
                        required=False)
        parser.set_defaults(manage_master=False)
        return parser

    def take_action(self, parsed_args):
        param_mapping = {
            'name': 'repo_name',
            'url': 'git_url',
            'ref': 'ref',
            'manage_master': 'manage_master',
        }

        data = {}
        for param, value in parsed_args.__dict__.items():
            if value is not None and param in param_mapping.keys():
                data[param_mapping[param]] = value
        repos = fc_client.get_request('/clusters/git-repos/')
        env = [repo['env_id'] for repo in repos
               if repo['id'] == parsed_args.repo][0]
        path = "/clusters/{0}/git-repos/{1}"

        if parsed_args.key:
            with open(parsed_args.key) as key_file:
                data['user_key'] = key_file.read()

        fc_client.put_request(path.format(env, parsed_args.repo), data)
        return (self.columns, data)


class InitRepo(command.Command):
    columns = (
        'id'
    )

    def get_parser(self, prog_name):
        parser = super(InitRepo, self).get_parser(prog_name)
        parser.add_argument('--repo',
                            type=int,
                            help='Repo ID to init',
                            required=True)
        return parser

    def take_action(self, parsed_args):
        repo_id = parsed_args.repo
        repos = fc_client.get_request('/clusters/git-repos/')
        env = [repo['env_id'] for repo in repos
               if repo['id'] == parsed_args.repo][0]

        init_path = "/clusters/{0}/git-repos/{1}/init"
        fc_client.put_request(init_path.format(env, repo_id), {})
        return (self.columns, {})


class DownloadConfgs(command.Command):

    def get_parser(self, prog_name):
        parser = super(DownloadConfgs, self).get_parser(prog_name)
        parser.add_argument('--env', type=int, help='Env ID', required=False)

        parser.add_argument('--key_path',
                            type=str,
                            help='Path to nodes private key file',
                            required=False)

        parser.add_argument('--repo_dir',
                            type=str,
                            help='Directory to Git repo download',
                            default='/tmp/repos',
                            required=False)
        return parser

    def take_action(self, parsed_args):
        # TODO(dukov) REFACTORING of this ugly staff
        ext_settings = GitExtensionSettings().config
        key = parsed_args.key_path
        if not key:
            # NOTE(dukov) this locked with nailgun.
            from nailgun.settings import settings
            key = settings.SHOTGUN_SSH_KEY

        nodes = fc_client.get_request('nodes/')
        repos = fc_client.get_request('/clusters/git-repos/')
        if parsed_args.env:
            repos = [repo for repo in repos
                     if repo['env_id'] == parsed_args.env]

        if not os.path.exists(parsed_args.repo_dir):
            os.mkdir(parsed_args.repo_dir)

        for repo in repos:
            key_path = os.path.join(
                parsed_args.repo_dir,
                repo['repo_name'] + '.key')
            with open(key_path, 'w') as keyf:
                keyf.write(repo['user_key'])
            os.chmod(key_path, 0o600)

            ssh_cmd = 'ssh -o StrictHostKeyChecking=no -i ' + key_path
            repo_path = os.path.join(parsed_args.repo_dir, repo['repo_name'])
            if not os.path.exists(repo_path):
                os.environ['GIT_SSH_COMMAND'] = ssh_cmd
                gitrepo = Repo.clone_from(repo['git_url'], repo_path)
            else:
                gitrepo = Repo(repo_path)

            cfg_branch = repo['ref'] + '_configs'
            with gitrepo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                gitrepo.remotes.origin.fetch()
                if cfg_branch in gitrepo.heads:
                    commit = gitrepo.remotes.origin.fetch(refspec=cfg_branch)
                    commit = commit[0].commit
                    gitrepo.head.reference = commit
                    gitrepo.head.reset(index=True, working_tree=True)
                else:
                    gitrepo.git.checkout('--orphan', cfg_branch)
                    gitrepo.git.rm('-r', '-f', repo_path)

            nodes = [node for node in nodes
                     if node['cluster'] == repo['env_id']]

            for node in nodes:
                for params in ext_settings['resource_mapping'].values():
                    path = params['path']
                    target_path = os.path.join(
                        repo_path,
                        "node_{}_configs".format(node['id']),
                        os.path.basename(path)
                    )
                    with fabric.api.settings(
                        host_string=node['ip'],
                        key_filename=key,
                        timeout=10,
                        warn_only=True,
                        abort_on_prompts=True,
                    ):
                        try:
                            fabric.api.get(path, target_path)
                        except AttributeError:
                            pass
                        except SystemExit:
                            print("Err")
            if gitrepo.is_dirty(untracked_files=True):
                gitrepo.git.add('-A')
                gitrepo.git.commit('-m "Configs updated"')
                with gitrepo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                    push_result = gitrepo.remotes.origin.\
                        push(refspec='HEAD:' + cfg_branch)
                    print("Push result {}".format(push_result))
        return ((), {})


class AuditRun(lister.Lister, command.Command):
    columns = (
        'task_id',
    )

    def get_parser(self, prog_name):
        parser = super(AuditRun, self).get_parser(prog_name)
        parser.add_argument('repo',
                            type=int,
                            help='Associated Repo ID')
        return parser

    def take_action(self, parsed_args):
        repo_id = parsed_args.repo
        task_id = audit.audit_run(repo_id)
        data = {'task_id': task_id}
        data = data_utils.get_display_data_multi(self.columns, [data])
        return (self.columns, data)


class AuditEnforce(lister.Lister, command.Command):
    columns = ()

    def get_parser(self, prog_name):
        parser = super(AuditEnforce, self).get_parser(prog_name)
        parser.add_argument('repo',
                            type=int,
                            help='Associated Repo ID')
        return parser

    def take_action(self, parsed_args):
        repos = fc_client.get_request('/clusters/git-repos/')
        repo_id = parsed_args.repo
        audit_task_id = audit.audit_run(repo_id)
        audit_task = Task(audit_task_id)
        while audit_task.status == 'running':
            time.sleep(AUDIT_TASK_CHECK_INTERVAL)
        changes = audit.get_outofsync(repo_id, audit_task_id)
        if changes:
            changed_tasks = [c['task_id'] for c in changes]
            LOG.info(
                "Following tasks have outofsync resources: {tasks}".format(
                    tasks=set(changed_tasks)
                )
            )
            LOG.info(("To get the list of changes, run "
                      "fuel2 gitrepo outofsync --repo "
                      "{repo_id} {task_id}").format(repo_id=repo_id,
                                                   task_id=audit_task_id))
            env_id = [repo['env_id'] for repo in repos
                   if repo['id'] == parsed_args.repo][0]

            env = Environment(env_id)
            LOG.info("Starting enforce run on environment {eid}".format(
                eid=env_id
            ))
            enforce_task_id = env.redeploy_changes()
            enforce_task = audit.get_running_task('deployment')
            LOG.info("Enforce task id is {tid}".format(tid=enforce_task.id))
            while enforce_task.status == 'running':
                time.sleep(AUDIT_TASK_CHECK_INTERVAL)
            LOG.info("Enforce task status is {status}".format(
                status=enforce_task.status
            ))
        return ((), {})


class OutOfSyncResources(lister.Lister, command.Command):
    columns = (
        'task_id',
        'node_id',
        'resource'
    )

    def get_parser(self, prog_name):
        parser = super(OutOfSyncResources, self).get_parser(prog_name)
        parser.add_argument('--repo',
                            type=int,
                            help='Associated Repo ID to apply whitelist from')
        parser.add_argument('task_id',
                            type=int,
                            help='Task ID to lookup changes on')
        return parser

    def take_action(self, parsed_args):
        task_id = parsed_args.task_id
        changes = audit.get_outofsync(repo_id, task_id)

        data = data_utils.get_display_data_multi(self.columns, changes)
        return (self.columns, data)
