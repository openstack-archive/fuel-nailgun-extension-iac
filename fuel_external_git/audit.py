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


import logging
import time


from fuelclient import client
if hasattr(client, 'DefaultAPIClient'):
    # Handling python-fuelclient version >= 10.0
    fc_client = client.DefaultAPIClient
else:
    # Handling python-fuelclient version <= 9.0
    fc_client = client.APIClient
from fuelclient.objects import Environment
from fuelclient.objects import Task


LOG = logging.getLogger(__name__)
TASK_RETRIES = 10
TASK_RETRY_DELAY = 2
TASK_HISTORY_URL = 'transactions/{tid}/deployment_history?include_summary=1'


def audit_run(repo_id):
    repos = fc_client.get_request('/clusters/git-repos/')
    env_id = [repo['env_id'] for repo in repos
           if repo['id'] == repo_id][0]

    env = Environment(env_id)
    # Due to how Nailgun handles such tasks, returned
    # one will not contain any deployment-related data.
    # So we'll have to fetch the last noop task with progress < 100
    LOG.info("Starting noop run on environment {eid}".format(eid=env_id))
    deploy_task = env.redeploy_changes(noop_run=True)
    task = get_running_task('dry_run_deployment')
    LOG.info("Noop task id is {tid}".format(tid=task.id))
    return task.id


def get_running_task(name):
    for retry in xrange(TASK_RETRIES):
        tasks = Task.get_all()
        try:
            task = filter(lambda t: t.data['status'] == 'running' and \
                          t.data['name'] == name,
                          tasks).pop()
            break
        except (IndexError) as e:
            time.sleep(TASK_RETRY_DELAY)
            continue
    return task



def get_outofsync(repo_id, task_id):
    repos = fc_client.get_request('/clusters/git-repos/')
    fuel_task = Task(task_id)

    history = fuel_task.connection.get_request(
        TASK_HISTORY_URL.format(tid=task_id)
    )
    changes = []
    changed_tasks = filter(lambda t: t['status'] != 'skipped' and \
                           t.get('summary', {}) and \
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
    
