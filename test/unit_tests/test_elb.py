#!/usr/bin/python3

from nose.tools import *
from troposphere import Template, Ref
from amazonia.classes.elb import Elb
import re


def test_protocol_to_upper():
    """
    Test to check upper and lower case protocol inputs match the beginning pf Target Address
    e.g. HTTP or http matches HTTP:80/index.html
    """
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


def test_subnets():
    """
    Tests to check list of subnets returns list of Refs to subnets
    e.g. [subnet1, subnet2] creates [Ref(subnet1), Ref(subnet2)]
    """
    helper_elb = create_elb(protocol='HTTP')
    assert_equals(helper_elb.elb.Subnets, [Ref('subnet-123456'), Ref('subnet-123496'), Ref('subnet-123454')])


def test_security_group():
    """
    Test to assert type of SecurityGroup equals Ref
    """
    helper_elb = create_elb(protocol='HTTP')
    print('type = {0}').format(type(helper_elb.elb.SecurityGroups))
    print('typeref = {0}').format(Ref)
    assert_is(type(helper_elb.elb.SecurityGroups), Ref)


def create_elb(**kwargs):
    """
    Helper function to create Elb Troposhpere object to interate through.
    :return: Troposphere object for Elb,
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
