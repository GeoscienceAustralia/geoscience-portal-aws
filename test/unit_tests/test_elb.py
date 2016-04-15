#!/usr/bin/python3

from nose.tools import *
from troposphere import Template, Ref
from amazonia.classes.elb import Elb
import re


def create_elb(**kwargs):
    """
    Helper function to create Elb Troposhpere object to interate through.
    :param port - port for traffic
    :param protocol: protocol for traffic
    :param path2ping: path to test page
    :return: Troposphere object for Elb,
    """
    vpc = 'vpc-12345'
    pub_sub_list = ['subnet-123456', 'subnet-123496', 'subnet-123454']
    elb = Elb(title='elb',
              port=kwargs.get('port', '80'),
              subnets=pub_sub_list,
              protocol=kwargs.get('protocol', 'HTTP'),
              vpc=vpc,
              hosted_zone_name=kwargs.get('hosted_zone_name', None),
              path2ping=kwargs.get('path2ping', 'index.html'),
              template=Template())
    return elb


def test_protocol_to_upper():
    """
    Test to check upper and lower case 'protocol' inputs match the beginning of Target Address
    e.g. HTTP or http matches HTTP:80/index.html
    Also tests that protocol matches Listener Protocol and Instance Protocol
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
                for listener in helper_elb.elb.Listeners:
                    assert_equal(upper_protocol, listener.Protocol)
                    assert_equal(upper_protocol, listener.InstanceProtocol)

        helper_test_protocol_to_upper(key, values)


def test_target():
    """
    Tests to make sure that inputs of 'protocol', 'port' and 'path2ping' correctly forms target healthcheck url
    """
    helper_elb = create_elb(protocol='HTTPS',
                            port='443',
                            path2ping='/test/index.html')
    assert_equals('HTTPS:443/test/index.html', helper_elb.elb.HealthCheck.Target)


def test_ports():
    """
    Tests to validate that passing in 'port' correctly sets the port in all the right places:
    'HealthCheck.Target', 'Listner.LoadBalancerPort', 'Listners.InstancePort'
    """
    ports = ['8080', '80', '443', '5678', '-1', '99', '65535']

    for port in ports:
        helper_elb = create_elb(port=port)
        assert_in(port, helper_elb.elb.HealthCheck.Target)
        for listener in helper_elb.elb.Listeners:
            assert_equal(port, listener.LoadBalancerPort)
            assert_equal(port, listener.InstancePort)


def test_subnets():
    """
    Tests to check list of subnets returns list of Refs to subnets
    e.g. [subnet1, subnet2] creates [Ref(subnet1), Ref(subnet2)]
    """
    helper_elb = create_elb()
    for subnet in helper_elb.elb.Subnets:
        assert_equals(type(subnet), Ref)


def test_security_group():
    """
    Test to assert type of SecurityGroup equals Ref
    """
    helper_elb = create_elb()
    print('type = {0}'.format(type(helper_elb.elb.SecurityGroups)))
    print('typeref = {0}'.format(Ref))
    for sg in helper_elb.elb.SecurityGroups:
        assert_is(type(sg), Ref)


def test_hosted_zone_name():
    helper_elb = create_elb(hosted_zone_name='myhostedzone.gadevs.ga.')
    assert helper_elb.elb_r53
