#!/usr/bin/python3

import yaml

"""
User values to be used for YAML ingestion and overwrite GA yaml_defaults
"""
import yaml

with open("./amazonia/classes/amazonia.yaml", 'r') as stack_yaml:
    try:
        print(yaml.load(stack_yaml))
        stack_data = yaml.load(stack_yaml)
    except yaml.YAMLError as exception:
        print(exception)



""" Validate YAML Values
"""

# def validate_stack_title(stack_title):
    # TODO stack_title must be alphanumeric

# def validate_cidr():
    # TODO cidr[0] must must cidr notation
    # TODO cidr[1] must be alphanumeric

# def unencrypted_access_keys():
    # TODO regex for enecrypted