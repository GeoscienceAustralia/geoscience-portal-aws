# pylint: disable=too-many-arguments, wildcard-import, unused-wildcard-import, line-too-long

"""

Templates to implement common cloud formation configurations

The functions in this module generate cloud formation scripts that install common AWS environments and components

"""

from troposphere import Template
from amazonia.amazonia_resources import *

def addVPC(template):
    """Create a VPC resource and add it to the given template."""
    vpc = add_vpc(template, VPC_CIDR)
    return vpc

class SingleAZenv(Template):
    """
    A working 'default' single AZ environment. Completely editable via troposphere commands.
    """

    def __init__(self, key_pair_name, invpc=""):
        """ Public Class to create a single AZ environment in a vpc """
        super(SingleAZenv, self).__init__()
        if invpc == "":
            self.vpc = addVPC(self)
        else:
            self.vpc = invpc

        # configure network
        self.public_subnet = add_subnet(self, self.vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
        self.public_route_table = add_route_table(self, self.vpc, "Public")
        add_route_table_subnet_association(self, self.public_route_table, self.public_subnet)

        self.internet_gateway = add_internet_gateway(self)
        self.internet_gateway_attachment = add_internet_gateway_attachment(self, self.vpc, self.internet_gateway)
        add_route_ingress_via_gateway(self, self.public_route_table, self.internet_gateway, PUBLIC_CIDR, dependson=[self.internet_gateway_attachment])
        self.private_subnet = add_subnet(self, self.vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ1_CIDR)
        self.private_route_table = add_route_table(self, self.vpc, "Private")
        add_route_table_subnet_association(self, self.private_route_table, self.private_subnet)

        # NAT Security Group
        self.nat_sg = add_security_group(self, self.vpc)
        # enable inbound http access to the NAT from anywhere
        add_security_group_ingress(self, self.nat_sg, 'tcp', '80', '80', cidr=PUBLIC_CIDR)
        # enable inbound https access to the NAT from anywhere
        add_security_group_ingress(self, self.nat_sg, 'tcp', '443', '443', cidr=PUBLIC_CIDR)
        # enable inbound SSH  access to the NAT from GA
        add_security_group_ingress(self, self.nat_sg, 'tcp', '22', '22', cidr=PUBLIC_COMPANY_CIDR)
        # enable inbound ICMP access to the NAT from anywhere
        add_security_group_ingress(self, self.nat_sg, 'icmp', '-1', '-1', cidr=PUBLIC_CIDR)

        self.nat = add_nat(self, self.public_subnet, key_pair_name, self.nat_sg)
        add_route_egress_via_NAT(self, self.private_route_table, self.nat, dependson=[self.internet_gateway_attachment])

class DualAZenv(Template):
    """
    A working 'default' dual AZ environment. Completely editable via troposphere commands.
    """

    def __init__(self, key_pair_name, invpc=""):
        """ Public Class to create a dual AZ environment in a vpc """
        super(DualAZenv, self,).__init__()
        if invpc == "":
            self.vpc = addVPC(self)
        else:
            self.vpc = invpc

        # AZ 1
        self.public_subnet1 = add_subnet(self, self.vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
        self.public_route_table = add_route_table(self, self.vpc, "Public")
        add_route_table_subnet_association(self, self.public_route_table, self.public_subnet1)
        self.internet_gateway = add_internet_gateway(self)
        self.internet_gateway_attachment = add_internet_gateway_attachment(self, self.vpc, self.internet_gateway)
        add_route_ingress_via_gateway(self, self.public_route_table, self.internet_gateway, PUBLIC_CIDR, dependson=[self.internet_gateway_attachment])
        self.private_subnet1 = add_subnet(self, self.vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ1_CIDR)
        self.private_route_table1 = add_route_table(self, self.vpc, "Private")
        add_route_table_subnet_association(self, self.private_route_table1, self.private_subnet1)

        # NAT Security Group
        self.nat_security_group = add_security_group(self, self.vpc)
        # enable inbound http access to the NAT from anywhere
        add_security_group_ingress(self, self.nat_security_group, 'tcp', '80', '80', cidr=PUBLIC_CIDR)
        # enable inbound https access to the NAT from anywhere
        add_security_group_ingress(self, self.nat_security_group, 'tcp', '443', '443', cidr=PUBLIC_CIDR)
        # enable inbound SSH  access to the NAT from GA
        add_security_group_ingress(self, self.nat_security_group, 'tcp', '22', '22', cidr=PUBLIC_COMPANY_CIDR)
        # enable inbound ICMP access to the NAT from anywhere
        add_security_group_ingress(self, self.nat_security_group, 'icmp', '-1', '-1', cidr=PUBLIC_CIDR)

        self.nat1 = add_nat(self, self.public_subnet1, key_pair_name, self.nat_security_group)
        add_route_egress_via_NAT(self, self.private_route_table1, self.nat1, dependson=[self.internet_gateway_attachment])

        switch_availability_zone()

        # AZ 2
        self.public_subnet2 = add_subnet(self, self.vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ2_CIDR)
        # Note below how we associate public subnet 2 to the single public route table we create for the VPC
        add_route_table_subnet_association(self, self.public_route_table, self.public_subnet2)

        self.private_subnet2 = add_subnet(self, self.vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ2_CIDR)
        self.private_route_table2 = add_route_table(self, self.vpc, "Private")
        add_route_table_subnet_association(self, self.private_route_table2, self.private_subnet2)

        self.nat2 = add_nat(self, self.public_subnet2, key_pair_name, self.nat_security_group)
        add_route_egress_via_NAT(self, self.private_route_table2, self.nat2, dependson=[self.internet_gateway_attachment])


class Env(Template):
    """
    A working 'default' Dual AZ VPC environment. Completely editable via troposphere commands.
    """

    def __init__(self):
        """ Public Class to create a dual AZ VPC with subnets """
        super(Env, self).__init__()
        self.vpc = addVPC(self)

        self.internet_gateway = add_internet_gateway(self)
        self.internet_gateway_attachment = add_internet_gateway_attachment(self, self.vpc, self.internet_gateway)

        # AZ 1
        self.public_subnet1 = add_subnet(self, self.vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
        self.public_route_table = add_route_table(self, self.vpc, "Public")
        add_route_table_subnet_association(self, self.public_route_table, self.public_subnet1)
        add_route_ingress_via_gateway(self, self.public_route_table, self.internet_gateway, PUBLIC_CIDR, dependson=[self.internet_gateway_attachment])

        self.private_subnet1 = add_subnet(self, self.vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ1_CIDR)
        self.private_route_table1 = add_route_table(self, self.vpc, "Private")
        add_route_table_subnet_association(self, self.private_route_table1, self.private_subnet1)

        switch_availability_zone()  # AZ 2

        self.public_subnet2 = add_subnet(self, self.vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ2_CIDR)
        add_route_table_subnet_association(self, self.public_route_table, self.public_subnet2)

        self.private_subnet2 = add_subnet(self, self.vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ2_CIDR)
        self.private_route_table2 = add_route_table(self, self.vpc, "Private")
        add_route_table_subnet_association(self, self.private_route_table2, self.private_subnet2)


class EnvNat(Env):
    """
    A working 'default' Dual AZ VPC environment. Completely editable via troposphere commands.
    """

    def __init__(self, key_pair_name):
        """ Public Class to create a dual AZ environment in a vpc """
        super(EnvNat, self).__init__()

        # NAT Security Group
        self.nat_security_group = add_security_group(self, self.vpc)
        add_security_group_ingress(self, self.nat_security_group, 'tcp', '80', '80', cidr=PUBLIC_CIDR)  # enable inbound http access to the NAT from anywhere
        add_security_group_ingress(self, self.nat_security_group, 'tcp', '443', '443', cidr=PUBLIC_CIDR)  # enable inbound https access to the NAT from anywhere
        add_security_group_ingress(self, self.nat_security_group, 'tcp', '22', '22', cidr=PUBLIC_COMPANY_CIDR)  # enable inbound SSH  access to the NAT from GA
        add_security_group_ingress(self, self.nat_security_group, 'icmp', '-1', '-1', cidr=PUBLIC_CIDR)  # enable inbound ICMP access to the NAT from anywhere
        self.nat1 = add_nat(self, self.public_subnet1, key_pair_name, self.nat_security_group)
        add_route_egress_via_NAT(self, self.private_route_table1, self.nat1, dependson=[self.internet_gateway_attachment])

        switch_availability_zone()  # AZ 2

        self.nat2 = add_nat(self, self.public_subnet2, key_pair_name, self.nat_security_group)
        add_route_egress_via_NAT(self, self.private_route_table2, self.nat2, dependson=[self.internet_gateway_attachment])

