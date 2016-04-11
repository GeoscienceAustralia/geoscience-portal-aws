#!/usr/bin/python3

import yaml
from amazonia.classes.yaml import Yaml


def main():
    with open('./test/sys_tests/amazonia.yaml', 'r') as stack_yaml:
        user_stack_data = yaml.load(stack_yaml)
        print('\nuser_stack_data=\n{0}\n'.format(user_stack_data))

    with open('./test/sys_tests/amazonia_ga_defaults.yaml', 'r') as default_yaml:
        default_data = yaml.load(default_yaml)
        print('\ndefault_data=\n{0}\n'.format(default_data))

    yaml_return = Yaml(user_stack_data, default_data)
    stack_input = yaml_return.united_data

    print('\nstack_input=\n{0}\n'.format(stack_input))

if __name__ == "__main__":
    main()
