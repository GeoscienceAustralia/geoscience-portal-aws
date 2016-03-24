# pylint: disable=too-many-arguments, line-too-long

from amazonia.amazonia_resources import *


class Elb(SecurityEnabledObject):
    def __init__(self, **kwargs):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(SecurityEnabledObject, self).__init__()

        self.elb = add_load_balancer()


        # TODO Elb Unit Tests:
        # TODO Unit Tests:jump_sg = jumphost1.NetworkInterfaces.GroupSet,
        # TODO Sys Tests: Connect from jumphost to subpub1 instance, subpub2 instance, can't connect on port 80,8080,443
        # TODO Sys Tests: Try connecting to host in another vpc

