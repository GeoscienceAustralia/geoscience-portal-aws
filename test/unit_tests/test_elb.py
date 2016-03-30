#!/usr/bin/python3

from nose.tools import *
from troposphere import Template
from amazonia.classes.elb import Elb
import re


def test_protocol_to_upper():
    protocols = {'HTTP': ['HTTP', 'http'],
                 'HTTPS': ['HTTPS', 'https'],
                 'TCP': ['TCP', 'tcp'],
                 'SSL': ['SSL', 'ssl']}

    for key, values in protocols.items():

        def helper_test_protocol_to_upper(upper_protocol, protocol_list):
            for protocol in protocol_list:
                helper_elb = create_elb(protocol=protocol)
                assert_true(re.match(upper_protocol, helper_elb.elb.HealthCheck.Target))

        helper_test_protocol_to_upper(key, values)

# TODO def test_path2ping():
#
#
# TODO def test_health_check_target():
#
#
# TODO def test_subnets():
#
#
# TODO def test_security_group():
#
#
# TODO def test_public_or_private():
#
#
#


def create_elb(**kwargs):
    """
    Helper function to create Single instance Troposhpere object to interate through.
    :param title: name of instance
    :return: Troposphere object for single instance, security group and output
    """
    vpc = 'vpc-12345'
    pub_sub_list = ['subnet-123456', 'subnet-123496', 'subnet-123454']
    elb = Elb(title='elb',
              port='80',
              subnets=pub_sub_list,
              protocol=kwargs['protocol'],
              vpc=vpc,
              path2ping='index.html',
              stack=Template())
    return elb
