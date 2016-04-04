#!/usr/bin/python3

from nose.tools import *
from troposphere import Template, Ref
from amazonia.classes.subnet import Subnet


def test_pub_or_pri():
    """ Validate that public/private subnet is correctly identified from route_table
    """


def test_subnet_title():
    """ Validate that subnet title is correctly created base don inputs
    """


def test_sub_cidr():
    """ Validate that subnet CIDR is correctly created for private/public subnets, number of subnet
    """


def test_add_associate_route_table():
    """ Validate route association created
    """


def test_az_num():
    """ Validate number of subnets for a Single, Dual and Triple AZ senario
    """


def create_subnets(**kwargs):
    """
    Helper function to create subnet objects.
    :return: Troposphere object for subnet,
    """

    stack = Template()
    stack.vpc = 'vpc-12345'
    stack.pub_route_table = 'MyUnitPublicRouteTable'
    stack.pri_route_table = 'MyUnitPrivateRouteTable'
    stack.pri_sub_list = stack.pub_sub_list = []
    az = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']

    subnet = Subnet(az=kwargs.get('az', az),
                    stack=stack,
                    route_table=kwargs.get('route_table', stack.pub_route_table))
    return subnet
