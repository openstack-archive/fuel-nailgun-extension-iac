import ConfigParser


class OpenStackConfig(object):
    def __init__(self, config_file, resource_name):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        # TODO(dukov) resource name can differ from filename
        self.config_name = "{}_config".\
                           format("".join(resource_name.split('.')[:-1]))

    def to_config_dict(self):
        """Function returns OpenStack config file in dictionary form
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
