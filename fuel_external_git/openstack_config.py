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

import ConfigParser
import os

from nailgun.logger import logger


class OpenStackConfig(object):
    def __init__(self, config_file, resource_name=None):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        if resource_name:
            self.config_name = resource_name
        else:
            file_name = os.path.basename(config_file)
            self.config_name = "{}_config".format(file_name.split('.')[:-1])
        logger.debug("Initalized Config {0}. Config resource name {1}.".
                     format(config_file, self.config_name))

    def to_config_dict(self):
        """Config transformation

           Function returns OpenStack config file in dictionary form
           compatible with override_configuration resource in
           fuel-library
           Example:
               {
                   "nova_config": {
                       DEFAULT/debug: {value: True}
                       DEFAULT/amqp_durable_queues: {value: False}
                   }
                }
        """
        config_resource = {}
        default_items = set(self.config.items('DEFAULT'))
        for section in self.config.sections():
            # Config prasee includes all items from DEFAULT secton
            # into items for each section. We need to exclude them
            section_content = set(self.config.items(section)) - default_items
            for key, value in section_content:
                params = {'value': value}
                config_resource["{0}/{1}".format(section, key)] = params

        # Add parameters from DEFAULT section
        for key, value in default_items:
            config_resource["DEFAULT/{}".format(key)] = {'value': value}

        return config_resource
