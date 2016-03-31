#!/usr/bin/python3

from nose.tools import *
from troposphere import Template, Ref
from amazonia.classes.elb import Elb


def create_elb(**kwargs):
    """
    Helper function to create Elb Troposhpere object to interate through.
    :return: Troposphere object for Elb,
    """
    vpc = 'vpc-12345'
    pub_sub_list = ['subnet-123456', 'subnet-123496', 'subnet-123454']
    elb = Elb(title='elb',
              port=kwargs.get('port', '80'),
              subnets=pub_sub_list,
              protocol=kwargs.get('protocol', 'HTTP'),
              vpc=vpc,
              path2ping=kwargs.get('path2ping', 'index.html'),
              stack=Template())
    return elb
