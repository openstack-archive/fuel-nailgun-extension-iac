import os

from nailgun.logger import logger
from fuel_external_git.openstack_config import OpenStackConfig


def get_config_hash(file_dir, resource_mapping):
    res = {}
    if not os.path.isdir(file_dir):
        logger.debug(
            "Directory {} not found. Returning emty dict".format(file_dir))
        return {}

    conf_files = [conf for conf in os.listdir(file_dir)
                  if conf.endswith('conf')]
    for conf_file in conf_files:
        # TODO(dukov) Config resource name may differ from file name
        config = OpenStackConfig(os.path.join(file_dir, conf_file),
                                 resource_mapping)
        res[config.config_name] = config.to_config_dict()
    return res


def deep_merge(dct, merge_dct):
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)):
            deep_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
