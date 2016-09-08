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

import copy
from fuel_external_git.tests import base
from fuel_external_git import utils


class TestUtils(base.TestCase):
    def test_extension_list(self):
        mapping = {
            'ceilometer_api_paste_ini': {
                'alias': 'ceilometer-api-paste.ini',
                'path': '/etc/ceilometer/api-paste.ini',
            },
            'ceilometer': {
                'alias': 'ceilometer.conf',
                'path': '/etc/ceilometer/ceilometer.conf',
            }
        }
        ext_list = utils.get_file_exts_list(mapping)
        self.assertEqual(ext_list, set(['ini', 'conf']))

    def test_deep_merge_two_empy(self):
        a = {}
        b = {}
        utils.deep_merge(a, b)
        self.assertEqual(a, {})

    def test_deep_merge_one_empy(self):
        sample_dict = {
            'a': {'b': {'c': 'd'}},
            'e': {'f': {'g': 'h'}},
        }
        new_dict = copy.deepcopy(sample_dict)
        utils.deep_merge(new_dict, {})
        self.assertEqual(new_dict, sample_dict)

        new_dict = {}
        utils.deep_merge(new_dict, sample_dict)
        self.assertEqual(new_dict, sample_dict)

    def test_merge_two_discts(self):
        a = {
            'a': {'b': {'c': 'd'}},
            'e': {'f': {'g': 'h'}},
        }

        b = {
            'x': {'b': {'c': 'd'}},
            'y': {'f': {'g': 'h'}},
        }

        result = {
            'a': {'b': {'c': 'd'}},
            'e': {'f': {'g': 'h'}},
            'x': {'b': {'c': 'd'}},
            'y': {'f': {'g': 'h'}},
        }

        utils.deep_merge(a, b)
        self.assertEqual(a, result)
