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

import os

from fuel_external_git.drivers.openstack_config import OpenStackConfig
from fuel_external_git.tests import base


class TestOpenStackConfig(base.TestCase):

    def test_dict_generation(self):
        resource = {
            'nova_config': {
                'DEFAULT/global_param': {
                    'value': 'global_param'
                },
                'DEFAULT/global_param_to_override': {
                    'value': 'global_param_to_override'
                },
            }
        }
        file_name = os.path.join(self.cfg_sample_dir, 'nova.conf')
        cfg = OpenStackConfig(file_name, self.config['resource_mapping'])
        self.assertEqual(cfg.to_config_dict(), resource)
