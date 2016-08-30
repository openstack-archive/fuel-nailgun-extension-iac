import os
import yaml

from nailgun.logger import logger


class GitExtensionSettings(object):
    def __init__(self):
        settings_files = []
        project_path = os.path.dirname(__file__)
        project_settings_file = os.path.join(project_path, 'settings.yaml')
        settings_files.append(project_settings_file)
        settings_files.append('/etc/git-exension-settings.yaml')
        settings_files.append('/etc/nailgun/git-exension-settings.yaml')
        self.config = {}
        for sf in settings_files:
            try:
                logger.debug("Trying to read config file %s" % sf)
                with open(sf) as custom_config:
                    self.config.update(yaml.load(custom_config.read()))
            except Exception as e:
                logger.error("Error while reading config file %s: %s" %
                             (sf, str(e)))
