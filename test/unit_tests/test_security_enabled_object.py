#!/usr/bin/python3

from amazonia.classes.security_enabled_object import SecurityEnabledObject
from nose.tools import *
from troposphere import Template, ec2


def test_security_enabled_object():
    """
    Test title, security group title, template
    """
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)

    assert_equals(myobj.title, "Unit01Web")
    assert_equals(myobj.security_group.title, "Unit01WebSg")
    assert_equals(myobj.template, template)


def test_create_sg():
    """
    Test security group title, Group Description
    """
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)

    assert_equals(myobj.security_group.title, "Unit01WebSg")
    assert_equals(myobj.security_group.GroupDescription, "Security group")
    # TODO find and implement a way test ref objects so we can test security_group.VpcId


def test_add_flow():
    """
    Test ingress and egress rules are correctly applied betwen two security groups
    """
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)
    otherobj = SecurityEnabledObject(title="Unit02Web", vpc=myvpc, template=template)

    myobj.add_flow(otherobj, '80')

    assert_equals(otherobj.ingress[0].title, "Unit02Web80FromUnit01Web80")
    assert_equals(otherobj.ingress[0].IpProtocol, "tcp")
    assert_equals(otherobj.ingress[0].FromPort, "80")
    assert_equals(otherobj.ingress[0].ToPort, "80")

    assert_equals(myobj.egress[0].title, "Unit01Web80ToUnit02Web80")
    assert_equals(myobj.egress[0].IpProtocol, "tcp")
    assert_equals(myobj.egress[0].FromPort, "80")
    assert_equals(myobj.egress[0].ToPort, "80")


def test_add_ingress():
    """
    Test ingress rules are correctly applied to security group
    """
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)
    otherobj = SecurityEnabledObject(title="Unit02Web", vpc=myvpc, template=template)

    myobj.add_ingress(otherobj, '80')

    assert_equals(myobj.ingress[0].title, "Unit01Web80FromUnit02Web80")
    assert_equals(myobj.ingress[0].IpProtocol, "tcp")
    assert_equals(myobj.ingress[0].FromPort, "80")
    assert_equals(myobj.ingress[0].ToPort, "80")


def test_add_ip_ingress():
    """
    Test ingress rules are correctly applied to CIDRs, elbs, single instances (nat or jump)
    """
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)

    cidrs = [{'name': 'GA1', 'cidr': '123.123.132.123/24'},
             {'name': 'GA2', 'cidr': '321.321.321.321/32'},
             {'name': 'PublicIp', 'cidr': '0.0.0.0/0'}]

    for num, cidr in enumerate(cidrs):
        myobj.add_ingress(cidr, port='80')
        assert_equals(myobj.ingress[num].title, 'Unit01Web80From{0}80'.format(cidr['name']))
        assert_equals(myobj.ingress[num].IpProtocol, 'tcp')
        assert_equals(myobj.ingress[num].FromPort, '80')
        assert_equals(myobj.ingress[num].ToPort, '80')


def test_add_ip_egress():
    """
    Test egress rules are correctly applied to CIDRs, elbs, single instances (nat or jump)
    """
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)

    cidrs = [{'name': 'GA1', 'cidr': '123.123.132.123/24'},
             {'name': 'GA2', 'cidr': '321.321.321.321/32'},
             {'name': 'PublicIp', 'cidr': '0.0.0.0/0'}]

    for num, cidr in enumerate(cidrs):
        myobj.add_egress(cidr, port='80')
        assert_equals(myobj.egress[num].title, 'Unit01Web80To{0}80'.format(cidr['name']))
        assert_equals(myobj.egress[num].IpProtocol, 'tcp')
        assert_equals(myobj.egress[num].FromPort, '80')
        assert_equals(myobj.egress[num].ToPort, '80')


def test_add_egress():
    """
    Test egress rules are correctly applied to security group
    """
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title='Unit01Web', vpc=myvpc, template=template)
    otherobj = SecurityEnabledObject(title='Unit02Web', vpc=myvpc, template=template)

    myobj.add_egress(otherobj, '80')

    assert_equals(myobj.egress[0].title, 'Unit01Web80ToUnit02Web80')
    assert_equals(myobj.egress[0].IpProtocol, 'tcp')
    assert_equals(myobj.egress[0].FromPort, '80')
    assert_equals(myobj.egress[0].ToPort, '80')


# def test_ip():
#     """
#     Tests that the function correctly substitutes punctuation in ip addresses. '.' becomes 'o', '/' becomes 'x'
#     """
#     cidrs = ['124.47.122.122/32', '324.47.122.12/24', '10.0.0.1/16', '12.34.56', '12.34.56.25']
#     expected_cidrs = ['124o47o122o122x32', '324o47o122o12x24', '10o0o0o1x16', '12o34o56', '12o34o56o25']
#     for num, cidr in enumerate(cidrs):
#         new_ip = SecurityEnabledObject.ip(cidr)
#         assert_equals(new_ip, expected_cidrs[num])
