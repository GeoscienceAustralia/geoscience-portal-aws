#!/usr/bin/python3
"""
Ingest User YAML and GA defaults YAML
Overwrite GA defaults YAML with User YAML

"""
import re
from iptools.ipv4 import validate_cidr


class Yaml(object):
    def __init__(self, stack_data, default_data):
        """
        :param stack_data: User yaml document used to read stack values
        :param default_data: Company yaml to read in company default values
        :return: Cloud Formation template
        """
        self.stack_data = stack_data
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

        for value in stack_value_list:
            self.united_data[value] = self.get_values(value)

        unit_value_list = ['unit_title',
                           'protocol',
                           'port']

        for unit_title, unit_values in self.get_values('units').items():
            self.united_data['units'][unit_title] = unit_title
            for unit_value in unit_value_list:
                self.united_data['units'][unit_title][unit_value] = self.get_values(unit_values)

        print(self.united_data)

        """ Validate Data
        """
        self.validate_title(self.united_data['stack_title'])                        # Validate stack title
        validate_cidr(self.united_data['vpc_cidr'])                                 # Validate VPC CIDR

        [self.validate_title(cidr[0]) for cidr in self.united_data['home_cidr']]    # Validate title of home_cidr tuple items
        [validate_cidr(cidr[1]) for cidr in self.united_data['home_cidr']]          # validate CIDR of home_cidr tuple items

        return self.united_data

    def get_values(self, value):
        united_value = self.stack_data.get(value, self.default_data[value])
        return united_value

    """ Validate YAML Values
    """
    @staticmethod
    def validate_title(stack_or_unit_title):
        pattern = re.compile('[\W_]+')                          # pattern is one or more non work characters
        pattern.sub('', stack_or_unit_title.printable)          # Regex sub nothing '' for pattern match
        return pattern


    # def unencrypted_access_keys():
        # TODO regex for enecrypted


