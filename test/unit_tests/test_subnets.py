#!/usr/bin/python3

from nose.tools import *
from troposphere import Template, ec2, Ref
from amazonia.classes.subnet import Subnet

def setup_resources():
    """ Sets Up stack resources
    """
    global stack, pub_route_table, pri_route_table, az
    stack = Template()
    stack.pri_sub_list = []
    stack.pub_sub_list = []
    stack.vpc = stack.add_resource(ec2.VPC('MyVPC',
                                           CidrBlock='10.0.0.0/16'))
    stack.pub_route_table = stack.add_resource(ec2.RouteTable('MyUnitPublicRouteTable',
                                                              VpcId=Ref(stack.vpc)))
    stack.pri_route_table = stack.add_resource(ec2.RouteTable('MyUnitPrivateRouteTable',
                                                              VpcId=Ref(stack.vpc)))
    az = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']

    # TODO change test referencing stack.pri_sub_list to pri_sub_list after tempalte refactor same with route tables

@with_setup(setup_resources)
def test_pub_or_pri():
    """ Validate that public/private subnet is correctly identified from route_table
    """

    for a in az:
        # For public subnets
        helper_pub_subnet = create_subnet(stack=stack, az=a, route_table=stack.pub_route_table)
        assert_equals(helper_pub_subnet.pub_or_pri, 'Public')

        # For private subnets
        helper_pri_subnet = create_subnet(stack=stack, az=a, route_table=stack.pri_route_table)
        assert_equals(helper_pri_subnet.pub_or_pri, 'Private')


@with_setup(setup_resources)
def test_sub_cidr():
    """ Validate that subnet CIDR is correctly created for private/public subnets for number of availablity zones
    """
    for num in range(len(az)):
        # For public subnets
        helper_pub_subnet = Subnet.sub_cidr(stack, 'Public')
        stack.pub_sub_list.append(helper_pub_subnet)
        assert_equals(helper_pub_subnet, ''.join(['10.0.', str(num), '.0/24']))

        # For private subnets
        helper_pri_subnet = Subnet.sub_cidr(stack, 'Private')
        stack.pri_sub_list.append(helper_pri_subnet)
        assert_equals(helper_pri_subnet, ''.join(['10.0.', str(num + 100), '.0/24']))


def test_add_associate_route_table():
    """ Validate route association created
    """
    for a in az:
        # For public subnets
        helper_pub_subnet = create_subnet(stack=stack, az=a, route_table=stack.pub_route_table)
        assert_true(helper_pub_subnet.rt_association)
        assert_equals(type(helper_pub_subnet.rt_association.RouteTableId), type(Ref(stack.pub_route_table)))
        assert_equals(type(helper_pub_subnet.rt_association.SubnetId), type(Ref(helper_pub_subnet)))
        assert_equals(helper_pub_subnet.rt_association.title,
                      stack.pub_route_table.title + helper_pub_subnet.subnet.title + 'Association')

        # For private subnets
        helper_pri_subnet = create_subnet(stack=stack, az=a, route_table=stack.pri_route_table)
        assert_true(helper_pri_subnet.rt_association)
        assert_equals(type(helper_pri_subnet.rt_association.RouteTableId), type(Ref(stack.pri_route_table)))
        assert_equals(type(helper_pri_subnet.rt_association.SubnetId), type(Ref(helper_pri_subnet)))
        assert_equals(helper_pri_subnet.rt_association.title,
                      stack.pri_route_table.title + helper_pri_subnet.subnet.title + 'Association')


def az_num(az_list):
    """ Helper function to validate number of subnets for a Single, Dual and Triple AZ senario passed in from test_az_num()
    """
    setup_resources()
    pub_subnets = []
    pri_subnets = []
    for a in az_list:
        pub_subnets.append(create_subnet(stack=stack, az=a, route_table=stack.pub_route_table))  # Append Public subnet
        pri_subnets.append(create_subnet(stack=stack, az=a, route_table=stack.pri_route_table))  # Append Private subnet
    assert_equals(len(az_list), len(pub_subnets))
    assert_equals(len(az_list), len(pri_subnets))


def test_az_num():
    """ Validate number of subnets for a Single, Dual and Triple AZ senario passing to az_num(az_list) to validate length
    """
    az_list = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']
    while len(az_list) > 0:
        print(len(az_list))
        az_num(az_list)
        az_list.pop()


def create_subnet(**kwargs):
    """
    Helper function to create subnet objects.
    :return: Troposphere object for subnet,
    """

    subnet = Subnet(az=kwargs.get('az', 'ap-southeast-2a'),
                    stack=kwargs['stack'],
                    route_table=kwargs['route_table'])

    return subnet
