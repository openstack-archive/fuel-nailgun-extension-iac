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
from oslo_utils import importutils

from nailgun.logger import logger


def get_file_exts_list(resource_mapping):
    return set(map(lambda key: key.split('.')[-1], resource_mapping.keys()))


def get_config_hash(file_dir, resource_mapping, exts=['conf']):
    res = {}
    if not os.path.isdir(file_dir):
        logger.debug(
            "Directory {} not found. Returning emty dict".format(file_dir))
        return {}

    conf_files = [conf for conf in os.listdir(file_dir)
                  if conf.split('.')[-1] in exts]

    for conf_file in conf_files:
        if conf_file in resource_mapping.keys():
            drv = resource_mapping[conf_file].get(
                'driver',
                'fuel_external_git.drivers.openstack_config.OpenStackConfig'
            )
            drv_class = importutils.import_class(drv)
            config = drv_class(
                os.path.join(file_dir, conf_file),
                resource_mapping[conf_file]['resource']
            )
            deep_merge(res, config.to_config_dict())
    return res


def deep_merge(dct, merge_dct):
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)):
            deep_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
