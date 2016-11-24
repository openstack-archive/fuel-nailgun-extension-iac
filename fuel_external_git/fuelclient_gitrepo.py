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

from cliff import command
from cliff import lister

from fuelclient import client
from fuelclient.common import data_utils
if hasattr(client, 'DefaultAPIClient'):
    # Handling python-fuelclient version >= 10.0
    fc_client = client.DefaultAPIClient
else:
    # Handling python-fuelclient version <= 9.0
    fc_client = client.APIClient


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
