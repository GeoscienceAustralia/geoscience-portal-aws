from nose.tools import *
from amazonia.classes.yaml import Yaml
import string


def test_validate_title():
    test_strings = ['test_Stack', 'test*String', 'test0String', 'test-string_']

    for test_string in test_strings:
        new_string = Yaml.validate_title(test_string)
        print('new_string={0}'.format(new_string))
        assert_true(ch in string.printable for ch in new_string)


# def test_validate_cidr():
#     test_cidrs = ['test_Stack', 'test*String', 'test0String', 'test-string_']
#
#     for test_cidr in test_cidrs:
#         new_cidr = Yaml.v