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

import logging
import time

from cliff import command
from cliff import lister

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

from fuel_external_git.const import AUDIT_TASK_CHECK_INTERVAL
from fuel_external_git.const import TASK_RETRIES
from fuel_external_git.const import TASK_RETRY_DELAY


LOG = logging.getLogger(__name__)


class Audit(lister.Lister, command.Command):
    columns = ()

    @staticmethod
    def get_running_task(name):
        for retry in xrange(TASK_RETRIES):
            tasks = Task.get_all()
            try:
                task = filter(lambda t: t.data['status'] == 'running' and
                              t.data['name'] == name,
                              tasks).pop()
                break
            except IndexError:
                time.sleep(TASK_RETRY_DELAY)
                continue
        return task

    @staticmethod
    def start_noop_run(env):
        # Due to how Nailgun handles such tasks, returned
        # one will not contain any deployment-related data.
        # So we'll have to fetch the last noop task with progress < 100
        env.redeploy_changes(noop_run=True)
        return Audit.get_running_task('dry_run_deployment')

    @staticmethod
    def get_outofsync(noop_task):
        history = noop_task.connection.get_request(
            ('transactions/{tid}/'
             'deployment_history?include_summary=1').format(tid=noop_task.id)
        )
        changes = []
        changed_tasks = filter(lambda t: t['status'] != 'skipped' and
                               t.get('summary', {}) and
                               t['summary']['resources']['out_of_sync'] > 0,
                               history)
        for task in changed_tasks:
            name = task['task_name']
            for item in task['summary']['raw_report']:
                if 'Would have triggered' not in item['message'] and \
                    'Finished catalog run' not in item['message']:
                    short_item = item['source'].replace('/Stage[main]/', '')
                    changes.append({'task_id': name,
                                    'resource': short_item,
                                    'node_id': task['node_id']})
        return changes

    def get_parser(self, prog_name):
        parser = super(Audit, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--env',
                           type=int,
                           help='Environment ID')
        group.add_argument('--repo',
                           type=int,
                           help='Associated Repo ID')
        return parser

    def take_action(self, parsed_args):
        env_id = parsed_args.env
        if not env_id:
            repo_id = parsed_args.repo
            repos = fc_client.get_request('/clusters/git-repos/')
            env_id = [repo['env_id'] for repo in repos
                      if repo['id'] == repo_id][0]

        env = Environment(env_id)

        audit_task = Audit.start_noop_run(env)

        LOG.info("Noop task ID is {tid}".format(tid=audit_task.id))

        while audit_task.status == 'running':
            time.sleep(AUDIT_TASK_CHECK_INTERVAL)
            LOG.info(
                'Current task progress is {p}'.format(p=audit_task.progress)
            )

        changes = Audit.get_outofsync(audit_task)

        if changes:
            changed_tasks = [c['task_id'] for c in changes]
            LOG.info(
                "Following tasks have outofsync resources: {tasks}".format(
                    tasks=set(changed_tasks)
                )
            )
            LOG.info(("To get the list of changes, run "
                      "fuel2 audit get outofsync --task "
                      "{task_id}").format(task_id=audit_task.id))
            LOG.info("Starting enforce run on environment {eid}".format(
                eid=env_id
            ))
            env.redeploy_changes()
            enforce_task = Audit.get_running_task('deployment')
            LOG.info("Enforce task id is {tid}".format(tid=enforce_task.id))
            while enforce_task.status == 'running':
                time.sleep(AUDIT_TASK_CHECK_INTERVAL)
                LOG.info(
                    'Current task progress is {p}'.format(
                        p=enforce_task.progress
                    )
                )
            LOG.info("Enforce task status is {status}".format(
                status=enforce_task.status
            ))
        return ((), {})


class AuditRun(lister.Lister, command.Command):
    columns = (
        'task_id',
    )

    def get_parser(self, prog_name):
        parser = super(AuditRun, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--env',
                           type=int,
                           help='Associated Repo ID')
        group.add_argument('--repo',
                           type=int,
                           help='Associated Repo ID')
        return parser

    def take_action(self, parsed_args):
        env_id = parsed_args.env
        if not env_id:
            repo_id = parsed_args.repo
            repos = fc_client.get_request('/clusters/git-repos/')
            env_id = [repo['env_id'] for repo in repos
                      if repo['id'] == repo_id][0]

        env = Environment(env_id)
        task = Audit.start_noop_run(env)

        data = {'task_id': task.id}
        data = data_utils.get_display_data_multi(self.columns, [data])
        return (self.columns, data)


class OutOfSyncResources(lister.Lister, command.Command):
    columns = (
        'task_id',
        'node_id',
        'resource'
    )

    def get_parser(self, prog_name):
        parser = super(OutOfSyncResources, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--env',
                           type=int,
                           help='Environment to lookup changes on')
        group.add_argument('--task',
                           type=int,
                           help='Task ID to lookup changes on')
        return parser

    def take_action(self, parsed_args):
        task_id = parsed_args.task
        if not task_id:
            all_tasks = Task.get_all()
            env_tasks = filter(
                lambda t: t.data['cluster'] == parsed_args.env and
                t.data['name'] == 'dry_run_deployment',
                all_tasks)
            env_tasks.sort(key=lambda t: t.data['time_start'])
            fuel_task = env_tasks[-1]
        else:
            fuel_task = Task(task_id)

        changes = Audit.get_outofsync(fuel_task)

        data = data_utils.get_display_data_multi(self.columns, changes)
        return (self.columns, data)


class WhitelistRulesShow(lister.Lister, command.Command):
    columns = (
        'id',
        'rule'
    )

    def get_parser(self, prog_name):
        parser = super(WhitelistRulesShow, self).get_parser(prog_name)
        parser.add_argument('env',
                            type=int,
                            help=('Environment to find whitelist rules '
                                  'associated with'))
        return parser

    def take_action(self, parsed_args):
        env_id = parsed_args.env

        rules = fc_client.get_request(
            '/clusters/{env}/changes-whitelist/'.format(env=env_id)
        )

        data = data_utils.get_display_data_multi(self.columns, rules)
        return (self.columns, data)


class WhitelistRuleAdd(lister.Lister, command.Command):
    columns = (
        'id',
        'rule'
    )

    def get_parser(self, prog_name):
        parser = super(WhitelistRuleAdd, self).get_parser(prog_name)
        parser.add_argument('env',
                            type=int,
                            help='Environment to add whitelist rules to')
        parser.add_argument('rule',
                            type=str,
                            help='Rule to add')
        return parser

    def take_action(self, parsed_args):
        env_id = parsed_args.env
        rule = parsed_args.rule
        data = {'rule': rule}

        ret = fc_client.post_request(
            '/clusters/{env}/changes-whitelist/'.format(env=env_id),
            data
        )
        ret = data_utils.get_display_data_multi(self.columns, ret)

        return (self.columns, ret)


class WhitelistRuleDelete(command.Command):
    columns = ()

    def get_parser(self, prog_name):
        parser = super(WhitelistRuleDelete, self).get_parser(prog_name)
        parser.add_argument('rule_id',
                            type=int,
                            help='Rule ID to delete')
        return parser

    def take_action(self, parsed_args):
        rule_id = parsed_args.rule_id

        fc_client.delete_request(
            '/clusters/changes-whitelist/{rule}'.format(rule=rule_id)
        )

        return ((), {})
