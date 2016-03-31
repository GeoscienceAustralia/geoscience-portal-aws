#!/usr/bin/python3

from nose.tools import *
from troposphere import Template, Ref
from amazonia.classes.elb import Elb


def create_subnets(**kwargs):
    """
    Helper function to create subnet objects.
    :return: Troposphere object for subnet,
    """
    vpc = 'vpc-12345'
    subnet = ''
    return subnet
