#!/usr/bin/python3

from amazonia.classes.securityenabledobject import SecurityEnabledObject
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


def test_add_si_ingress():
    """
    Test ingress rules are correctly applied to single instances (nat or jump)
    """
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)

    myobj.add_si_ingress('0.0.0.0/0', '80')

    assert_equals(myobj.ingress[0].title, "Unit01Web80From0o0o0o0x080")
    assert_equals(myobj.ingress[0].IpProtocol, "tcp")
    assert_equals(myobj.ingress[0].FromPort, "80")
    assert_equals(myobj.ingress[0].ToPort, "80")


def test_add_si_egress():
    """
    Test ingress rules are correctly applied to single instances (nat or jump)
    """
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)

    myobj.add_si_egress('0.0.0.0/0', '80')

    assert_equals(myobj.egress[0].title, "Unit01Web80To0o0o0o0x080")
    assert_equals(myobj.egress[0].IpProtocol, "tcp")
    assert_equals(myobj.egress[0].FromPort, "80")
    assert_equals(myobj.egress[0].ToPort, "80")


def test_add_egress():
    """
    Test egress rules are correctly applied to security group
    """
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)
    otherobj = SecurityEnabledObject(title="Unit02Web", vpc=myvpc, template=template)

    myobj.add_egress(otherobj, "80")

    assert_equals(myobj.egress[0].title, "Unit01Web80ToUnit02Web80")
    assert_equals(myobj.egress[0].IpProtocol, "tcp")
    assert_equals(myobj.egress[0].FromPort, "80")
    assert_equals(myobj.egress[0].ToPort, "80")


def test_ip():
    """
    Tests that the function correctly substitutes punctuation in ip addresses. '.' becomes 'o', '/' becomes 'x'
    """
    cidrs = ['124.47.122.122/32', '324.47.122.12/24', '10.0.0.1/16', '12.34.56', '12.34.56.25']
    expected_cidrs = ['124o47o122o122x32', '324o47o122o12x24', '10o0o0o1x16', '12o34o56', '12o34o56o25']
    for num, cidr in enumerate(cidrs):
        new_ip = SecurityEnabledObject.ip(cidr)
        assert_equals(new_ip, expected_cidrs[num])
