#!/usr/bin/python3

from nose.tools import *
from amazonia.classes.yaml import Yaml
import string
import yaml

stack_input = yaml_return = None


def setup_resources():
    """
    Create User data and default data yaml and send them to yaml class to be combined as united_data
    :return: Nothing, but creates united_data a combined list of user and default data
    """
    global stack_input, yaml_return
    with open('./test/unit_tests/amazonia.yaml', 'r') as stack_yaml:
        user_stack_data = yaml.load(stack_yaml)
        print('\nuser_stack_data=\n{0}\n'.format(user_stack_data))

    with open('./test/unit_tests/amazonia_ga_defaults.yaml', 'r') as default_yaml:
        default_data = yaml.load(default_yaml)
        print('\ndefault_data=\n{0}\n'.format(default_data))

    yaml_return = Yaml(user_stack_data, default_data)

    stack_input = yaml_return.united_data
    print('\nstack_input=\n{0}\n'.format(stack_input))


@with_setup(setup_resources())
def test_get_values():
    """
    Validated that Yaml.get_values (done during setup) is correctly returning expected values in users stack_yaml
    and where it is missing it using the default_data value (e.g. in keypair)
    """
    nat_instance_type = stack_input['nat_instance_type']
    assert_equals(nat_instance_type, 't2.micro')

    keypair = stack_input['keypair']
    assert_equals(keypair, 'pipeline')


@with_setup(setup_resources())
def test_get_unit_values():
    """

    """
    minsize = stack_input['units'][0]['minsize']
    assert_equals(minsize, '1')

    port = stack_input['units'][0]['port']
    assert_equals(port, '80')


def test_validate_title():
    """
    Tests validate_title function that returns string without any non alphanumeric data
    """
    test_strings = ['test_Stack', 'test*String', 'test0String', 'test-string_']

    for test_string in test_strings:
        new_string = Yaml.validate_title(test_string)
        print('new_string={0}'.format(new_string))
        assert_true(ch in string.printable for ch in new_string)


@with_setup(setup_resources())
def test_units():
    """
    Validate unit yaml value is a list of dictionaries
    Validate that unit value exists in expected list of unit values
    """
    unit_key_list = yaml_return.unit_key_list

    """ Assert units is of type list
    """
    assert_equals(type(stack_input['units']), list)

    """ Assert unit is of type dictionary
    """
    for unit in stack_input['units']:
        assert_equals(type(unit), dict)
        """
        Create counter dictionary, Assert unit_key is part of unit key list, delete from counter dictionary,
        Assert no values of united unit values remain after deleting them after verifying their existence
        in amazonia's expected unit_key_list
        """
        counter = {unit_key: unit_value for unit_key, unit_value in unit.items()}
        for unit_key in unit:
            assert_in(unit_key, unit_key_list)
            del counter[unit_key]

        assert_equals(len(counter), 0)


@with_setup(setup_resources())
def test_stack_value():
    """
    Validate stack yaml value is a list of dictionaries
    Validate that stack value exists in expected list of stack values
    :return:
    """
    stack_key_list = yaml_return.stack_key_list

    """ Assert stack values are of type dict
    """
    assert_equals(type(stack_input), dict)

    """
    Create counter dictionary, Assert stack_key is part of stack key list, delete from counter dictionary,
    Assert no values of united stack values remain after deleting them after verifying their existence
    in amazonia's expected stack_key_list
    """
    counter = {unit_key: unit_value for unit_key, unit_value in stack_input.items()}
    for stack_key, stack_value in stack_input.items():
        assert_in(stack_key, stack_key_list)
        del counter[stack_key]

    assert_equals(len(counter), 0)


@with_setup(setup_resources())
def test_unencrypted_ids():
    userdata1 = stack_input['units'][0]['userdata']
    assert_equals(userdata1, 'AWS_ACCESS_ID_FOUND')


@with_setup(setup_resources())
def test_unencrypted_keys():
    userdata2 = stack_input['units'][1]['userdata']
    assert_equals(userdata2, 'AWS_SECRET_KEY_FOUND')


@with_setup(setup_resources())
def validate_home_cidrs():
    cidr = stack_input['home_cidrs'][0]
    assert_equals(cidr, 'INVALID_CIDR')


@with_setup(setup_resources())
def test_validate_cidr():
    cidr = stack_input['vpc_cidr']
    assert_equals(cidr, 'INVALID_CIDR')
