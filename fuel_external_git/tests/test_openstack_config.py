import os

from fuel_external_git.tests import base
from fuel_external_git.openstack_config import OpenStackConfig


class TestOpenStackConfig(base.TestCase):

    def test_dict_generation(self):
        resource = {
            'DEFAULT/global_param': {
                'value': 'global_param'
            },
            'DEFAULT/global_param_to_override': {
                'value': 'global_param_to_override'
            },
        }
        file_name = os.path.join(self.cfg_sample_dir, 'nova.conf')
        cfg = OpenStackConfig(file_name, self.config['resource_mapping'])
        self.assertEqual(cfg.to_config_dict(), resource)
