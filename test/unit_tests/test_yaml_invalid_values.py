#!/usr/bin/python3

from nose.tools import *
from amazonia.classes.yaml import Yaml
import yaml
import os

stack_input = yaml_return = None


def setup_resources():
    """
    Create User data and default data yaml and send them to yaml class to be combined as united_data
    """
    global stack_input, yaml_return
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, 'amazonia.yaml'), 'r') as stack_yaml:
        user_stack_data = yaml.load(stack_yaml)
        print('\nuser_stack_data=\n{0}\n'.format(user_stack_data))

    with open(os.path.join(__location__, 'amazonia_ga_defaults.yaml'), 'r') as default_yaml:
        default_data = yaml.load(default_yaml)
        print('\ndefault_data=\n{0}\n'.format(default_data))

    yaml_return = Yaml(user_stack_data, default_data)

    stack_input = yaml_return.united_data
    print('\nstack_input=\n{0}\n'.format(stack_input))


@with_setup(setup_resources())
def test_get_values():
    """
    Testing for multiple conditions:
        Valid values in stack_key_list
        Valid values in unit_key_list
        Invalid values in stack_key_list
        Invalid values in unit_key_list
    """
    invalid_stack_values = {'invalid_value': 'what',
                            'mistake': 'this is a mistake',
                            'not_even_a_value': 'not_in_yaml'}
    invalid_unit_values = {'first_test_prop': 'tester',
                           'test_prop': '34',
                           'another_test_prop': 'wer'}
    valid_stack_values = {'jump_image_id': 'ami-893f53b3',
                          'nat_image_id': 'ami-893f53b3',
                          'vpc_cidr': '10.0.0.0.0/16'}
    valid_unit_values = {'unit_title': 'app1',
                         'protocol': 'HTTP',
                         'minsize': '1'}

    [assert_in(k, yaml_return.stack_key_list) for k, _ in valid_stack_values.items()]
    [assert_in(k, yaml_return.unit_key_list) for k, _ in valid_unit_values.items()]
    [assert_not_in(k, yaml_return.stack_key_list) for k, _ in invalid_stack_values.items()]
    [assert_not_in(k, yaml_return.unit_key_list) for k, _ in invalid_unit_values.items()]


