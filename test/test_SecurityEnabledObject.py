from amazonia.classes.securityenabledobject import SecurityEnabledObject
from nose.tools import *
from troposphere import ec2

def test_security_enabled_object():
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web" ,vpc=myvpc)
    assert_equals(myobj.security_group)

def test_create_sg()
    asd


def test_add_flow():
    asd


def test_add_ingress():
    asd


def test_add_egress():
    asd
