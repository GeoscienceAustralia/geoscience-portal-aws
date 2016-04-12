#!/usr/bin/python3
"""
Ingest User YAML and GA defaults YAML
Overwrite GA defaults YAML with User YAML

"""
import re
import string
import yaml
from iptools.ipv4 import validate_cidr


class Yaml(object):
    def __init__(self, user_stack_data, default_data):
        """
        :param user_stack_data: User yaml document used to read stack values
        :param default_data: Company yaml to read in company default values
        :return: Cloud Formation template
        """
        self.user_stack_data = user_stack_data
        self.default_data = default_data
        self.united_data = dict()
        self.set_values()

    def set_values(self):
        """ Assign values
        """
        stack_value_list = ['stack_title',
                            'code_deploy_service_role',
                            'keypair',
                            'availability_zones',
                            'vpc_cidr',
                            'jump_image_id',
                            'jump_instance_type',
                            'nat_image_id',
                            'nat_instance_type',
                            'home_cidr',
                            'units']

        for stack_value in stack_value_list:
            self.united_data[stack_value] = self.get_values(stack_value)

        unit_value_list = ['userdata',
                           'image_id',
                           'instance_type',
                           'path2ping',
                           'protocol',
                           'port',
                           'minsize',
                           'maxsize']

        for unit_title, unit_values in self.user_stack_data['units'].items():
            print('\nunit_title={0}\n'.format(unit_title))
            print('\nunit_values={0}\n'.format(unit_values))
            for unit_value in unit_value_list:
                self.united_data['units'][unit_title][unit_value] = self.get_unit_values(unit_title, unit_value)

        print('\nunited_data={0}\n'.format(self.united_data))

        """ Validate Data
        """
        self.validate_title(self.united_data['stack_title'])                          # Validate stack title
        validate_cidr(self.united_data['vpc_cidr'])                                 # Validate VPC CIDR

        # Validate title of home_cidr tuple items
        self.united_data['home_cidr'] = [(self.validate_title(cidr[0]), cidr[1]) for cidr in self.united_data['home_cidr']]

        [print(cidr[0]) for cidr in self.united_data['home_cidr']]    # Validate title of home_cidr tuple items


        # # validate for unecrypted aws access ids and aws secret keys
        # [self.unencrypted_access_keys(self.united_data['units'][unit]['userdata']) for unit in self.united_data['units']]
        # return self.united_data

    def get_values(self, value):
        """
        Set united value from user stack data otherwise use default data value
        :param value: yaml vlaue e.g. jump_image_id or port
        :return: United value using user yaml as overriding value from defaults
        """
        united_value = self.user_stack_data.get(value, self.default_data[value])
        return united_value

    def get_unit_values(self, unit_title, unit_value):
        """
        Set united value from user stack data otherwise use default data value
        :param unit_value: yaml vlaue e.g. jump_image_id or port
        :param unit_title: title of unit, which is key in user_stack_data dictionary
        :return: United value using user yaml as overriding value from defaults
        """
        united_value = self.user_stack_data['units'][unit_title].get(unit_value, self.default_data[unit_value])
        return united_value

    """ Validate YAML Values
    """
    @staticmethod
    def validate_title(stack_or_unit_title):
        pattern = re.compile('[\W_]+')                           # pattern is one or more non work characters
        new_title = pattern.sub('', stack_or_unit_title)         # Regex sub nothing '' for pattern match
        print('new_title={0}'.format(new_title))
        return new_title

    @staticmethod
    def unencrypted_access_keys(string):
        aws_access_id = re.compile('(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])')
        aws_secret_key = re.compile('(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])')

        if aws_access_id.search(string):
            return 'AWS ACCESS ID FOUND'
        elif aws_secret_key.search(string):
            return 'AWS SECRET KEY FOUND'
        else:
            return string
