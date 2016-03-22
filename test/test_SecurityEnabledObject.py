from amazonia.classes.securityenabledobject import SecurityEnabledObject
from nose.tools import *
from troposphere import ec2

def test_security_enabled_object():
    myvpc = ec2.VPC('myVpc', CidrBlock='10.0.0.0/16')
    myobj = SecurityEnabledObject(title="Unit01Web" ,vpc=myvpc)

    assert_equals(myobj.title, "Unit01Web")
    assert_equals(myobj.security_group.title, "Unit01WebSG")


def test_create_sg():
    # TODO test
    pass


def test_add_flow():
    # TODO test
    pass


def test_add_ingress():
    # TODO test
    pass


def test_add_egress():
    # TODO test
    pass
