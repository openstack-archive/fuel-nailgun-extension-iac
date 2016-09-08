#!/bin/env python
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

import argparse
import ConfigParser
import os
import sys
import yaml


def deep_merge(dct, merge_dct):
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)):
            deep_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def read_config_files(from_dir):
    confs = {}
    for config_file in os.listdir(from_dir):
        if config_file.endswith('conf'):
            cfg = ConfigParser.ConfigParser()
            cfg.read(os.path.join(from_dir, config_file))
            confs[config_file] = cfg

    return confs


def update_configs(orig, new):
    for file_name, cfg in new.items():
        global_cfg = orig.get(file_name, None)
        if global_cfg:
            deep_merge(global_cfg.__dict__, cfg.__dict__)
        else:
            orig[file_name] = cfg


def main(repo_path, dest_dir, role=None, node=None):
    overrides_file = os.path.join(repo_path, 'overrides.yaml')
    if not (os.path.exists(overrides_file) or role and node):
        print("There is no overrides.yaml file. But role or node specified")
        sys.exit(1)
    else:
        overrides = yaml.load(open(overrides_file))

    configs = read_config_files(repo_path)
    if role and overrides['roles'].get(role, None):
        cfg_path = os.path.join(repo_path, overrides['roles'][role])
        role_configs = read_config_files(cfg_path)
        update_configs(configs, role_configs)
    if node and overrides['nodes'].get(node, None):
        cfg_path = os.path.join(repo_path, overrides['nodes'][node])
        node_configs = read_config_files(cfg_path)
        update_configs(configs, node_configs)

    for file_name, cfg in configs.items():
        with open(os.path.join(dest_dir, file_name), 'w') as fd:
            cfg.write(fd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Configs')
    parser.add_argument('-s', '--src', dest='src', action='store',
                        help='Config Source dir', required=True)
    parser.add_argument('-d', '--dst', dest='dst', action='store',
                        help='Config Destination dir', required=True)
    parser.add_argument('-r', '--role', dest='role', action='store',
                        help='Generate configs for role')
    parser.add_argument('-n', '--node', dest='node', action='store',
                        help='Generate configs for node')
    parser.add_argument('-f', '--force', dest='force', action='store_true',
                        help='Force generate configs')

    args = parser.parse_args()

    if not args.force and args.node and not args.role:
        print(("You have to specify role for node to get full config file."
               " Use --force parameter to ignore this"))
        sys.exit(1)

    src = os.path.abspath(args.src)
    dst = os.path.abspath(args.dst)
    if not os.path.isdir(src):
        print("Source dir {} does not exists".format(args.src))
        sys.exit(1)
    if os.path.isdir(dst):
        print("Destination dir {} exists.".format(args.dst))
        print("Remove it to proceed or specify different path")
        sys.exit(1)
    else:
        os.mkdir(dst)

    main(src, dst, role=args.role, node=args.node)
