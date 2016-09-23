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

import yaml

from nailgun.logger import logger


class YamlConfig(object):
    def __init__(self, config_file, resource_name):
        with open(config_file) as cfg:
            self.config = yaml.load(cfg)
            self.config_name = resource_name

        logger.debug("Initalized Config {0}.".
                     format(config_file))

    def to_config_dict(self):
        return self.config
