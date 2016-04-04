#!/usr/bin/python3

from nose.tools import *
from troposphere import Template, ec2, Ref
from amazonia.classes.subnet import Subnet
import re


def test_pub_or_pri():
    """ Validate that public/private subnet is correctly identified from route_table
    """
    stack = Template()
    stack.pri_sub_list = stack.pub_sub_list = []
    stack.vpc = stack.add_resource(ec2.VPC('MyVPC',
                                           CidrBlock='10.0.0.0/16'))
    stack.pub_route_table = stack.add_resource(ec2.RouteTable('MyUnitPublicRouteTable',
                                                              VpcId=Ref(stack.vpc)))
    stack.pri_route_table = stack.add_resource(ec2.RouteTable('MyUnitPrivateRouteTable',
                                                              VpcId=Ref(stack.vpc)))
    az = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']

    for a in az:
        helper_pub_subnet = create_subnet(stack=stack, az=a, route_table=stack.pub_route_table)
        assert_equals(helper_pub_subnet.pub_or_pri, 'Public')
        helper_pri_subnet = create_subnet(stack=stack, az=a, route_table=stack.pri_route_table)
        assert_equals(helper_pri_subnet.pub_or_pri, 'Private')

#
# def test_subnet_title():
#     """ Validate that subnet title is correctly created base don inputs
#     """
#     pub_or_pri_list = ['Public', 'Private']
#     test_pub_or_pri()
#     for pub_or_pri in pub_or_pri_list:
#         assert_true(re.match(pub_or_pri, helper_pub_subnet.subnet.title))
#         assert_true(re.match(pub_or_pri, helper_pri_subnet.subnet.title))
#         assert_equals(az[-1:].upper(), helper_pri_subnet.subnet.title[-1:])
#
#
# def test_sub_cidr():
#     """ Validate that subnet CIDR is correctly created for private/public subnets, number of subnet
#     """
#     helper_pub_subnet = Subnet.sub_cidr(stack=stack, 'Public')
#     helper_pri_subnet = Subnet.sub_cidr(stack=stack, 'Private')
#     assert_equals(helper_pub_subnet, '10.0.0.0/24')
#     assert_equals(helper_pri_subnet, '10.0.0.0/24')
#
#
# def test_add_associate_route_table():
#     """ Validate route association created
#     """
#     helper_pub_subnet = create_subnet()
#     helper_pri_subnet = create_subnet()
#
#     assert_equals(helper_pub_subnet.rt_association.RouteTableId, Ref(stack.pub_route_table))
#     assert_equals(helper_pub_subnet.rt_association.SubnetId, Ref(helper_pub_subnet))
#
#     assert_equals(helper_pri_subnet.rt_association.RouteTableId, Ref(stack.pri_route_table))
#     assert_equals(helper_pri_subnet.rt_association.SubnetId, Ref(helper_pri_subnet))
#
#
# def test_az_num():
#     """ Validate number of subnets for a Single, Dual and Triple AZ senario
#     """
#     az_list =[1, 2, 3]
#
#     for az in az_list:
#         for a in az:
#             subnets =[]
#             subnets.append(create_subnet(az=a))
#             assert_equals(len(az),len(subnets))
#         az.pop(-1)


def create_subnet(**kwargs):
    """
    Helper function to create subnet objects.
    :return: Troposphere object for subnet,
    """

    subnet = Subnet(az=kwargs.get('az', 'ap-southeast-2a'),
                    stack=kwargs['stack'],
                    route_table=kwargs['route_table'])
    return subnet
