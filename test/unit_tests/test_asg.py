from nose.tools import *
from troposphere import Template
from amazonia.classes.asg import Asg


def test_asg():
    """
    Tests for instances where 'nat' is the first 3 letters  of the title and expect natting (SourceDestCheck)
    to be enabled and the PrivateIp to be displayed in the output.
    :return: Pass
    """
    pass
    assert_equals(create_asg(), "blah")


def create_asg():
    """
    Helper function to create ASG Troposhpere object.
    :return: Troposphere object for single instance, security group and output
    """
    template = Template()
    asg = Asg(stack=template)
    return asg
