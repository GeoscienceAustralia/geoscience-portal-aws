#!/usr/bin/python3

from amazonia.classes.securityenabledobject import SecurityEnabledObject
from nose.tools import *
from troposphere import Template, ec2


def test_security_enabled_object():
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, stack=template)

    assert_equals(myobj.title, "Unit01Web")
    assert_equals(myobj.security_group.title, "Unit01WebSG")
    assert_equals(myobj.stack, template)


def test_create_sg():
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, stack=template)

    assert_equals(myobj.security_group.title, "Unit01WebSG")
    assert_equals(myobj.security_group.GroupDescription, "Security group")
    # TODO find and implement a way test ref objects so we can test security_group.VpcId


def test_add_flow():
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, stack=template)
    otherobj = SecurityEnabledObject(title="Unit02Web", vpc=myvpc, stack=template)

    myobj.add_flow(otherobj, '80', 'tcp')

    assert_equals(otherobj.ingress.title, "Unit02Web80FromUnit01Web80")
    assert_equals(otherobj.ingress.IpProtocol, "tcp")
    assert_equals(otherobj.ingress.FromPort, "80")
    assert_equals(otherobj.ingress.ToPort, "80")

    assert_equals(myobj.egress.title, "Unit01Web80ToUnit02Web80")
    assert_equals(myobj.egress.IpProtocol, "tcp")
    assert_equals(myobj.egress.FromPort, "80")
    assert_equals(myobj.egress.ToPort, "80")


def test_add_ingress():
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, stack=template)
    otherobj = SecurityEnabledObject(title="Unit02Web", vpc=myvpc, stack=template)

    myobj.add_ingress(otherobj, '80', "tcp")

    assert_equals(myobj.ingress.title, "Unit01Web80FromUnit02Web80")
    assert_equals(myobj.ingress.IpProtocol, "tcp")
    assert_equals(myobj.ingress.FromPort, "80")
    assert_equals(myobj.ingress.ToPort, "80")


def test_add_egress():
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, stack=template)
    otherobj = SecurityEnabledObject(title="Unit02Web", vpc=myvpc, stack=template)

    myobj.add_egress(otherobj, "80", "tcp")

    assert_equals(myobj.egress.title, "Unit01Web80ToUnit02Web80")
    assert_equals(myobj.egress.IpProtocol, "tcp")
    assert_equals(myobj.egress.FromPort, "80")
    assert_equals(myobj.egress.ToPort, "80")
