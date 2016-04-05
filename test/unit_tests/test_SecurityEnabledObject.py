#!/usr/bin/python3

from amazonia.classes.securityenabledobject import SecurityEnabledObject
from nose.tools import *
from troposphere import Template, ec2


def test_security_enabled_object():
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)

    assert_equals(myobj.title, "Unit01Web")
    assert_equals(myobj.security_group.title, "Unit01WebSg")
    assert_equals(myobj.template, template)


def test_create_sg():
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)

    assert_equals(myobj.security_group.title, "Unit01WebSg")
    assert_equals(myobj.security_group.GroupDescription, "Security group")
    # TODO find and implement a way test ref objects so we can test security_group.VpcId


def test_add_flow():
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
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)
    otherobj = SecurityEnabledObject(title="Unit02Web", vpc=myvpc, template=template)

    myobj.add_ingress(otherobj, '80')

    assert_equals(myobj.ingress[0].title, "Unit01Web80FromUnit02Web80")
    assert_equals(myobj.ingress[0].IpProtocol, "tcp")
    assert_equals(myobj.ingress[0].FromPort, "80")
    assert_equals(myobj.ingress[0].ToPort, "80")


def test_add_egress():
    template = Template()
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)
    otherobj = SecurityEnabledObject(title="Unit02Web", vpc=myvpc, template=template)

    myobj.add_egress(otherobj, "80")

    assert_equals(myobj.egress[0].title, "Unit01Web80ToUnit02Web80")
    assert_equals(myobj.egress[0].IpProtocol, "tcp")
    assert_equals(myobj.egress[0].FromPort, "80")
    assert_equals(myobj.egress[0].ToPort, "80")
