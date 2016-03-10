# pylint: disable=too-many-arguments, line-too-long

from amazonia.amazonia_resources import *
from troposphere import Template


class Stack(Template):
    def __init__(self, invpc=""):
        """ Public Class to create a single AZ environment in a vpc """
        super(Stack, self).__init__()

        if invpc == "":
            self.vpc = addVPC(self)
        else:
            self.vpc = invpc

        switch_availability_zone(0)
        self.sub_pub1 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ1_CIDR) # TODO Change PUBLIC_SUBNET_AZ1_CIDR to subnet generator

        switch_availability_zone(1)
        self.sub_pub2 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ2_CIDR) # TODO Change PUBLIC_SUBNET_AZ2_CIDR to subnet generator

        switch_availability_zone(2)
        self.sub_pub3 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ3_CIDR) # TODO Change PUBLIC_SUBNET_AZ1_CIDR to subnet generator

        switch_availability_zone(0)
        self.sub_pri1 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ1_CIDR) # TODO Change PUBLIC_SUBNET_AZ1_CIDR to subnet generator

        switch_availability_zone(1)
        self.sub_pri2 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ2_CIDR) # TODO Change PUBLIC_SUBNET_AZ2_CIDR to subnet generator

        switch_availability_zone(2)
        self.sub_pri3 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ3_CIDR) # TODO Change PUBLIC_SUBNET_AZ1_CIDR to subnet generator
