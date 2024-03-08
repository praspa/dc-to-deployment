#!/usr/bin/env python3

import sys
import re
import yaml

class YamlTransform():

    def __init__(self, filename, keys_sub):
        self.filename = filename
        self.cbuffers = None
        self.keys_sub = keys_sub

    def transform(self):
        try:
            with open(self.filename, 'r') as file:
                buffers = yaml.safe_load_all(file)
                for buffer in buffers:
                    print('---')
                    print(yaml.dump(self._convert(buffer)))
        except IOError as e:
            print(help, file=sys.stderr)
            print(e, file=sys.stderr)
            exit(1)

    def _convert(self, buffer):
        for key in self.keys_sub:

            path = key['path'].split('.')
            path_len = len(path)
            pointer = buffer

            # Walks through the buffer tree and replaces the values in the "keys_sub" dictionary
            for idx, leaf in enumerate(path, start=1):

                if pointer.get(leaf) is None:
                    print('key: {} Not Found, skipping...'.format(key['path']), file=sys.stderr)
                    break

                if idx == path_len:

                    if key.get('remove'):
                        pointer.pop(leaf)
                    else:
                        if key.get('subs'):
                            for sub in key['subs']:
                                pointer[leaf] = re.sub(sub[0],sub[1],pointer[leaf])

                        if key.get('move'):
                            new_path_pointer = pointer
                            new_path = key['move'].split('.')
                            # this loop stops before reaching the last element
                            for idy in range(len(new_path)-1):
                                new_path_pointer[new_path[idy]] = new_path_pointer.get(new_path[idy], {})
                                new_path_pointer = new_path_pointer[new_path[idy]]
                            # the last element gets the value of the pointer
                            new_path_pointer[new_path[-1]] = pointer.pop(leaf)

                else:
                    pointer = pointer[leaf]

        return buffer

if __name__ == "__main__":
    help="Usage: {} [filename.yaml]".format(sys.argv[0])

    keys_sub = [
            {'path': 'apiVersion', 'subs': [['^apps.openshift.io/v1', 'apps/v1'],['^v1', 'apps/v1']]},
            {'path': 'kind', 'subs': [['^DeploymentConfig', 'Deployment']]},
            {'path': 'spec.strategy.type', 'subs': [['^Rolling', 'RollingUpdate']]},
            {'path': 'spec.strategy.activeDeadlineSeconds', 'remove': True},
            {'path': 'spec.strategy.resources', 'remove': True},
            {'path': 'spec.strategy.rollingParams.intervalSeconds', 'remove': True},
            {'path': 'spec.strategy.rollingParams.timeoutSeconds', 'remove': True},
            {'path': 'spec.strategy.rollingParams.updatePeriodSeconds', 'remove': True},
            {'path': 'spec.triggers', 'remove': True},
            {'path': 'spec.test', 'remove': True},
            {'path': 'spec.selector', 'move': 'selector.matchLabels'},
            {'path': 'spec.strategy.rollingParams', 'move': 'rollingUpdate'},
    ]

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print(help, file=sys.stderr)
        exit(1)

    yaml_transform = YamlTransform(filename, keys_sub)
    yaml_transform.transform()
