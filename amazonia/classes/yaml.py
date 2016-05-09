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
                               'home_cidrs',
                               'units']

        self.unit_key_list = ['unit_title',
                              'hosted_zone_name',
                              'userdata',
                              'image_id',
                              'instance_type',
                              'path2ping',
                              'protocols',
                              'loadbalancerports',
                              'instanceports',
                              'minsize',
                              'maxsize',
                              'health_check_grace_period',
                              'iam_instance_profile_arn',
                              'sns_topic_arn',
                              'sns_notification_types',
                              'elb_log_bucket',
                              'health_check_type']

        self.get_invalid_data()
        self.set_values()

    def get_invalid_data(self):
        """
        Validation Invalid Values in stack and unit yaml and exit if any exist
        """
        invalid_values = list()
        """ Delete valid values from stack_counter, a clone of stack keys value pairs"""
        stack_counter = {stack_key: stack_value for stack_key, stack_value in self.user_stack_data.items()}
        for stack_key in self.user_stack_data:
            if stack_key in self.stack_key_list:
                del stack_counter[stack_key]
        """ stack_counter should be zero if there are no invalid values otherwise add to invalid_values"""
        if len(stack_counter) > 0:
            invalid_values.append(stack_counter)

        """Iterate through N number of units"""
        for unit, unit_values in enumerate(self.user_stack_data['units']):
            unit_counter = {unit_key: unit_value for unit_key, unit_value in unit_values.items()}
            """ Delete valid values from unit_counter, a clone of unit keys value pairs"""
            for unit_key, unit_value in unit_values.items():
                if unit_key in self.unit_key_list:
                    del unit_counter[unit_key]
            """ unit_counter should be zero if there are no invalid values otherwise add to invalid_values"""
            if len(unit_counter) > 0:
                unit_counter['unit'] = unit
                invalid_values.append(unit_counter)

        """ Print All Invalid Values"""
        if len(invalid_values) > 0:
            print('Invalid Values Exist:\n{0}'.format(invalid_values))
            exit(1)

    def set_values(self):
        """
        Assigning values to the united_data dictionary
        Validating values such as vpc cidr, home cidrs, aws access ids and secret keys and reassigning if required
        """
        for stack_key in self.stack_key_list:
            """ Add stack key value pair to united data"""
            self.united_data[stack_key] = self.get_values(stack_key)
        """Iterate through N number of units"""
        for unit, unit_values in enumerate(self.user_stack_data['units']):
            """ Add stack key value pair to united data"""
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
        self.validate_home_cidrs(self.united_data['home_cidrs'])

        """ Validate title of home_cidrs tuple items
        """
        self.united_data['home_cidrs'] = \
            [(self.validate_title(cidr[0]), cidr[1]) for cidr in self.united_data['home_cidrs']]

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
        :return: Original userdata is no complaints, otherwise error string e.g. 'AWS_ACCESS_ID_FOUND' or
        'AWS_SECRET_KEY_FOUND'
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
                self.united_data['home_cidrs'][num] = cidr_title, 'INVALID_CIDR'
