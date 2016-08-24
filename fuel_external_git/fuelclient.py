from __future__ import absolute_import

from fuelclient.client import APIClient
from fuelclient.common import data_utils

from cliff import command
from cliff import lister


class GitRepoList(lister.Lister, command.Command):
    columns = (
        'id',
        'repo_name',
        'env_id',
        'git_url',
        'ref'
    )

    def get_parser(self, prog_name):
        parser = super(GitRepoList, self).get_parser(prog_name)
        parser.add_argument('--env', type=int, help='Env ID', required=False)
        return parser

    def take_action(self, parsed_args):
        data = APIClient.get_request('/clusters/git-repos/')
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
        'ref'
    )

    def get_parser(self, prog_name):
        parser = super(AddRepo, self).get_parser(prog_name)
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
        return parser

    def take_action(self, parsed_args):
        data = {
            'repo_name': parsed_args.name,
            'env_id': parsed_args.env,
            'git_url': parsed_args.url,
            'ref': parsed_args.ref,
        }

        if parsed_args.key:
            with open(parsed_args.key) as key_file:
                data['key'] = key_file.read()

        result = APIClient.post_request('/clusters/git-repos/', data)
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
            repos = APIClient.get_request('/clusters/git-repos/')
            env = [repo['env_id'] for repo in repos
                   if repo['id'] == parsed_args.repo][0]

        del_path = "/clusters/{0}/git-repos/{1}"
        result = APIClient.delete_request(del_path.format(env, repo_id))
        return (self.columns, {})


class UpdateRepo(command.Command):
    columns = (
        'id',
        'repo_name',
        'git_url',
        'ref'
    )

    def get_parser(self, prog_name):
        parser = super(UpdateRepo, self).get_parser(prog_name)
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
        return parser

    def take_action(self, parsed_args):
        param_mapping = {
            'name': 'repo_name',
            'url': 'git_url',
            'ref': 'ref',
        }

        data = {}
        for param, value in parsed_args.__dict__.items():
            if value and param in param_mapping.keys():
                data[param_mapping[param]] = value
        repos = APIClient.get_request('/clusters/git-repos/')
        env = [repo['env_id'] for repo in repos
               if repo['id'] == parsed_args.repo][0]
        path = "/clusters/{0}/git-repos/{1}"

        if parsed_args.key:
            with open(parsed_args.key) as key_file:
                data['key'] = key_file.read()

        APIClient.put_request(path.format(env, parsed_args.repo), data)
        return (self.columns, data)


class InitRepo(command.Command):
    columns = (
        'id'
    )

    def get_parser(self, prog_name):
        parser = super(InitRepo, self).get_parser(prog_name)
        parser.add_argument('--repo',
                            type=int,
                            help='Repo ID to delete',
                            required=True)
        return parser

    def take_action(self, parsed_args):
        repo_id = parsed_args.repo
        repos = APIClient.get_request('/clusters/git-repos/')
        env = [repo['env_id'] for repo in repos
               if repo['id'] == parsed_args.repo][0]

        init_path = "/clusters/{0}/git-repos/{1}/init"
        result = APIClient.put_request(init_path.format(env, repo_id), {})
        return (self.columns, {})
