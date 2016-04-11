#!/usr/bin/python3
"""
Ingest User YAML and GA defaults YAML and send to yaml class to return as one unified data dictionary for stack input

"""
import yaml
from amazonia.classes.yaml import Yaml
from amazonia.classes.stack import Stack


def read_yaml(user_yaml):
    """ Ingest user YAML
    """
    with open(user_yaml, 'r') as stack_yaml:
        print(stack_yaml)
        return yaml.load(stack_yaml)


def read_defaults(default_yaml):
    """ Ingest  GA default YAML
    """
    with open(default_yaml, 'r') as default_yaml:
        print(default_yaml)
        return yaml.load(default_yaml)


def create_stack(united_data):
    """
    Create Stack using amazonia
    :param united_data: Dictionary of yaml consisting of user yaml values with default yaml values for any missing keys
    return: Troposphere template object
    """

    stack = Stack(**united_data)

    """ Print Cloud Formation Template
    """
    print(stack.template.to_json(indent=2, separators=(',', ': ')))


def __main__():
    """
    Ingest User YAML as user_stack_data
    Ingest GA defaults YAML as default_data
    Create list of stack input dictoinary objects from yaml class
    create stack from stack input dictionary
    """
    user_stack_data = read_yaml('./amazonia/amazonia.yaml')
    default_data = read_defaults('./amazonia/amazonia_ga_defaults.yaml')

    stack_input = Yaml(user_stack_data, default_data)

    Stack(**stack_input.united_data)
