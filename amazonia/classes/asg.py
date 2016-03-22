# pylint: disable=too-many-arguments, line-too-long

from amazonia.amazonia_resources import *


class Asg(SecurityEnabledObject):
    def __init__(self, **kwargs):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(object, self).__init__()

        self.asg = add_security_group(self, self.vpc)

        # TODO ASG Unit Tests:

        # TODO Sys Tests:
