# pylint: disable=too-many-arguments, line-too-long

from amazonia.amazonia_resources import *
from troposphere import Template


class Stack(Template):
    def __init__(self, invpc=""):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(Stack, self).__init__()

        vpc_cidr = VPC_CIDR   # TODO Change VPC_CIDR to CIDR generator

        if invpc == "":
            self.vpc = add_vpc(self, vpc_cidr)
        else:
            self.vpc = invpc

        switch_availability_zone(0)
        self.sub_pub1 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ1_CIDR) # TODO Change PUBLIC_SUBNET_AZ1_CIDR to subnet generator /8

        switch_availability_zone(1)
        self.sub_pub2 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ2_CIDR) # TODO Change PUBLIC_SUBNET_AZ2_CIDR to subnet generator /8

        switch_availability_zone(2)
        self.sub_pub3 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ3_CIDR) # TODO Change PUBLIC_SUBNET_AZ1_CIDR to subnet generator /8

        switch_availability_zone(0)
        self.sub_pri1 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ1_CIDR) # TODO Change PUBLIC_SUBNET_AZ1_CIDR to subnet generator /8

        switch_availability_zone(1)
        self.sub_pri2 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ2_CIDR) # TODO Change PUBLIC_SUBNET_AZ2_CIDR to subnet generator /8

        switch_availability_zone(2)
        self.sub_pri3 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ3_CIDR) # TODO Change PUBLIC_SUBNET_AZ1_CIDR to subnet generator /8

        # TODO Routing Tables

        # TODO Internet Gateway
        self.internet_gateway = add_internet_gateway(self)
        self.internet_gateway_attachment = add_internet_gateway_attachment(self, self.vpc, self.internet_gateway)

        # TODO Jump Host
        # TODO Jump Host Security Group

        # TODO NAT
        # TODO NAT Security Group




