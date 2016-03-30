#!/usr/bin/python3

from nose.tools import *
from troposphere import Template
from amazonia.classes.elb import Elb


def test_protocol_to_upper():


def test_path2ping():


def test_health_check_target():


def test_subnets():


def test_security_group():


# def test_public_or_private():





def create_elb(title):
    """
    Helper function to create Single instance Troposhpere object to interate through.
    :param title: name of instance
    :return: Troposphere object for single instance, security group and output
    """
    vpc = 'vpc-12345'
    subnet = 'subnet-123456'
    template = Template()
    elb = Elb(title=title,
              keypair='pipeline',
              si_image_id='ami-893f53b3',
              si_instance_type='t2.nano',
              vpc=vpc,
              subnet=subnet,
              stack=template)
    return elb
