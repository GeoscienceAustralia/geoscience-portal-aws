#!/usr/bin/python3
"""
Ingest User YAML and GA defaults YAML
Overwrite GA defaults YAML with User YAML
"""
import re
from iptools.ipv4 import validate_cidr


class Yaml(object):
    """Setting these as class variables rather than instance variables so that they can be resolved and referred to
     statically"""
    unit_types = ['autoscaling_units', 'database_units']
    stack_key_list = ['stack_title',
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
                      'autoscaling_units',
                      'database_units']
    unit_key_list = {'autoscaling_units': ['unit_title',
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
                                           'health_check_type',
                                           'dependencies'],
                     'database_units': ['unit_title',
                                        'db_instance_type',
                                        'db_engine',
                                        'db_port',
                                        'dependencies']
                     }

    def __init__(self, user_stack_data, default_data):
        """
        :param user_stack_data: User yaml document used to read stack values
        :param default_data: Company yaml to read in company default values
        """
        self.user_stack_data = user_stack_data
        self.default_data = default_data
        self.united_data = dict()
        self.unit_key_list = dict()

        self.get_invalid_keys()
        self.set_values()

    def get_invalid_keys(self):
        """
        Detect Invalid keys in stack and unit yaml and raise error if any exist
        """
        self.get_invalid_values(self.user_stack_data, self.stack_key_list)

        for unit_type in self.unit_types:
            if unit_type in self.user_stack_data:
                for unit, unit_values in enumerate(self.user_stack_data[unit_type]):
                    self.get_invalid_values(unit_values, self.unit_key_list[unit_type])

    def set_values(self):
        """
        Assigning values to the united_data dictionary
        Validating values such as vpc cidr, home cidrs, aws access ids and secret keys and reassigning if required
        """
        for stack_key in self.stack_key_list:
            """ Add stack key value pairs to united data"""
            self.united_data[stack_key] = self.user_stack_data.get(stack_key, self.default_data[stack_key])

        """ Validate Stack Title
        """
        self.validate_title(self.united_data['stack_title'])

        """ Validate VPC CIDR
        """
        if not validate_cidr(self.united_data['vpc_cidr']):
            raise InvalidCidrError('Error: An invalid CIDR {0} was found.'.format('vpc_cidr'))

        """ Validate title and CIDRs of Home CIDRs list
        """
        for num, cidr in enumerate(self.united_data['home_cidrs']):
            if not validate_cidr(cidr[1]):
                raise InvalidCidrError('Error: An invalid CIDR {0} was found.'.format(cidr[0]))

        for unit_type in self.unit_types:
            if unit_type in self.user_stack_data:
                for unit, unit_values in enumerate(self.user_stack_data[unit_type]):
                    """ Add stack key value pair to united data"""
                    self.validate_title(self.united_data[unit_type][unit]['unit_title'])

                    for unit_value in self.unit_key_list:
                        """ Validate for unecrypted aws access ids and aws secret keys"""
                        if unit_value == 'userdata':
                            self.detect_unencrypted_access_keys(self.united_data[unit_type][unit]['userdata'])

                        self.united_data[unit_type][unit][unit_value] = \
                            self.user_stack_data[unit_type][unit].get(unit_value, self.default_data[unit_value])

    @staticmethod
    def validate_title(title):
        """
        Validate that the string passed in returns the same string stripped of non alphanumeric characters
        :param title: Title from the united_data yaml containing hte stack or unit title
        """
        pattern = re.compile('[\\W_]+')  # pattern is one or more non work characters

        if pattern.match(title):
            raise InvalidTitleError('Error: invalid characters used in stack or unit title: {0}'
                                    .format(pattern.match(title)))

    @staticmethod
    def detect_unencrypted_access_keys(userdata):
        """
        Searches userdata for potential AWS access ids and secret keys and substitutes entire userdata with error string
        :param userdata: Userdata for each unit in the stack
        """
        aws_access_id = re.compile('(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])')
        aws_secret_key = re.compile('(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])')

        if aws_access_id.search(userdata):
            raise InsecureVariableError('Error: unencrypted {0} was found in your userdata, please remove or encrypt.'
                                        .format('AWS access ID'))
        elif aws_secret_key.search(userdata):
            raise InsecureVariableError('Error: unencrypted {0} was found in your userdata, please remove or encrypt.'
                                        .format('AWS secret Key'))

    @staticmethod
    def get_invalid_values(user_key, key_list):
        """
        Uses set operations to detect invalid keys and throw an error when one is found
        :param user_key:
        :param key_list:
        """
        user_set = set(user_key)
        expected_set = set(key_list)
        invalid_set = user_set.difference(expected_set)
        if len(invalid_set) > 0:
            raise InvalidKeyError('Error: invalid keys {0} were found in your yaml, please remove or adjust.'
                                  .format('invalid_set'))


class InsecureVariableError(Exception):
    def __init__(self, value):
        self.value = value


class InvalidCidrError(Exception):
    def __init__(self, value):
        self.value = value


class InvalidKeyError(Exception):
    def __init__(self, value):
        self.value = value


class InvalidTitleError(Exception):
    def __init__(self, value):
        self.value = value
