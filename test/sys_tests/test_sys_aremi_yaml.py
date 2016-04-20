#!/usr/bin/python3

import yaml
import os
from amazonia.classes.yaml import Yaml
from amazonia.amz import create_stack


def main():
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, 'aremi.yaml'), 'r') as stack_yaml:
        user_stack_data = yaml.load(stack_yaml)

    with open(os.path.join(__location__, 'amazonia_ga_defaults.yaml'), 'r') as default_yaml:
        default_data = yaml.load(default_yaml)

    yaml_return = Yaml(user_stack_data, default_data)
    stack_input = yaml_return.united_data
    template_trop = create_stack(stack_input)
    print(template_trop.template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
