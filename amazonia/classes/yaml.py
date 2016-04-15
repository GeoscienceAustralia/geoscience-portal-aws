#!/usr/bin/python3
"""
Ingest User YAML and GA defaults YAML
Overwrite GA defaults YAML with User YAML
"""
import re
from iptools.ipv4 import validate_cidr


class Yaml(object):
    def __init__(self, user_stack_data, default_data):
        """
        :param user_stack_data: User yaml document used to read stack values
        :param default_data: Company yaml to read in company default values
        """
        self.user_stack_data = user_stack_data
        self.default_data = default_data
        self.united_data = dict()
        self.stack_key_list = list()
        self.unit_key_list = list()
        self.set_values()

    def set_values(self):
        """
        Assigning values to the united_data dictionary
        """
        self.stack_key_list = ['stack_title',
                               'code_deploy_service_role',
                               'keypair',
                               'availability_zones',
                               'vpc_cidr',
                               'public_cidr',
                               'jump_image_id',
                               'jump_instance_type',
                               'nat_image_id',
                               'nat_instance_type',
                               'home_cidr',
                               'units']

        for stack_value in self.stack_key_list:
            self.united_data[stack_value] = self.get_values(stack_value)

        self.unit_key_list = ['unit_title',
                              'userdata',
                              'image_id',
                              'instance_type',
                              'path2ping',
                              'protocol',
                              'port',
                              'minsize',
                              'maxsize']

        for unit, unit_values in enumerate(self.user_stack_data['units']):
            for unit_value in self.unit_key_list:
                self.united_data['units'][unit][unit_value] = self.get_unit_values(unit, unit_value)

        """ Validate Stack Title
        """
        self.united_data['stack_title'] = self.validate_title(self.united_data['stack_title'])

        """ Validate VPC CIDR
        """
        # TODO Requires Error handling
        if validate_cidr(self.united_data['vpc_cidr']) is False:
            self.united_data['vpc_cidr'] = 'INVALID_CIDR'

        """ Validate Home CIDRs
        """
        self.validate_home_cidrs(self.united_data['home_cidr'])

        """ Validate title of home_cidr tuple items
        """
        self.united_data['home_cidr'] = [(self.validate_title(cidr[0]), cidr[1]) for cidr in self.united_data['home_cidr']]

        """ Validate for unecrypted aws access ids and aws secret keys
        """
        for unit, unit_values in enumerate(self.united_data['units']):
            if self.unencrypted_access_keys(self.united_data['units'][unit]['userdata']) == 'AWS_ACCESS_ID_FOUND':
                self.united_data['units'][unit]['userdata'] = 'AWS_ACCESS_ID_FOUND'
            elif self.unencrypted_access_keys(self.united_data['units'][unit]['userdata']) == 'AWS_SECRET_KEY_FOUND':
                self.united_data['units'][unit]['userdata'] = 'AWS_SECRET_KEY_FOUND'

    def get_values(self, value):
        """
        Set united value from user stack data otherwise use default data value
        :param value: yaml vlaue e.g. jump_image_id or port
        :return: United value using user yaml as overriding value from defaults
        """
        united_value = self.user_stack_data.get(value, self.default_data[value])
        return united_value

    def get_unit_values(self, unit, unit_value):
        """
        Set united value from user stack data otherwise use default data value
        :param unit_value: Yaml vlaue e.g. jump_image_id or port
        :param unit: Position of unit in list of units, units is the key in user_stack_data dictionary
        :return: United value using user yaml as overriding value from defaults
        """
        united_value = self.user_stack_data['units'][unit].get(unit_value, self.default_data[unit_value])
        return united_value

    """ Validate YAML Values
    """
    @staticmethod
    def validate_title(stack_or_unit_title):
        """
        Validate that the string passed in returns the same string stripped of non alphanumeric characters
        :param stack_or_unit_title: Title from the united_data yaml containing hte stack or unit title
        :return: String stripped of non alphanumeric characters
        """
        pattern = re.compile('[\\W_]+')                           # pattern is one or more non work characters
        new_title = pattern.sub('', stack_or_unit_title)         # Regex sub nothing '' for pattern match
        return new_title

    @staticmethod
    def unencrypted_access_keys(userdata):
        """
        Searches userdata for potential AWS access ids and secret keys and substitutes entire userdata with error string
        :param userdata: Userdata for each unit in the stack
        :return: Original userdata is no complaints, otherwise error string e.g. 'AWS_ACCESS_ID_FOUND' or 'AWS_SECRET_KEY_FOUND'
        """
        aws_access_id = re.compile('(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])')
        aws_secret_key = re.compile('(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])')

        if aws_access_id.search(userdata):
            return 'AWS_ACCESS_ID_FOUND'
        elif aws_secret_key.search(userdata):
            return 'AWS_SECRET_KEY_FOUND'

    def validate_home_cidrs(self, home_cidrs):
        """
        Validates home_cidrs are looped through and each home_cidr's name and cidr is validated using prevoius functions
        :param home_cidrs: list of cidr tuples from unit_data yaml, tuple is in the form (name, cidr)
        """
        for num, cidr in enumerate(home_cidrs):
            if validate_cidr(cidr[1]) is False:
                cidr_title = self.validate_title(cidr[0])
                self.united_data['home_cidr'][num] = cidr_title, 'INVALID_CIDR'
