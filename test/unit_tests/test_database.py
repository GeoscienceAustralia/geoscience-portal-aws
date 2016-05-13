#!/usr/bin/python3

import re
from nose.tools import *
from troposphere import Template, Ref

from amazonia.classes.elb import Elb



def test_protocol():
    """
    Test to check that 'protocol' inputs match the beginning of Target Address
    e.g. HTTP matches HTTP:80/index.html
    Also tests that protocol matches Listener Protocol and Instance Protocol
    """
    protocols = ['HTTP', 'HTTPS', 'TCP', 'SSL']

    def helper_test_protocol(protocol_list):
        for protocol in protocol_list:
            helper_elb = create_elb(protocol=protocol)
            assert_true(re.match(protocol, helper_elb.trop_elb.HealthCheck.Target))
            for listener in helper_elb.trop_elb.Listeners:
                assert_equal(protocol, listener.Protocol)
                assert_equal(protocol, listener.InstanceProtocol)

    helper_test_protocol(protocols)
