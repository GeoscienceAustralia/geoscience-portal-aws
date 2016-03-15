# pylint: disable=too-many-arguments, line-too-long

from amazonia.amazonia_resources import *
from troposphere import Template


class Stack(Template):
    def __init__(self, invpc="", keypair_nat="", keypair_jump=""):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(Stack, self).__init__()

        vpc_cidr = VPC_CIDR   # TODO Change VPC_CIDR to CIDR generator

        if invpc == "":
            self.vpc = add_vpc(self, vpc_cidr)
        else:
            self.vpc = invpc

        switch_availability_zone(0)
        # TODO Change PUBLIC_SUBNET_AZ1_CIDR to subnet generator /24
        self.sub_pub1 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ1_CIDR)

        switch_availability_zone(1)
        # TODO Change PUBLIC_SUBNET_AZ2_CIDR to subnet generator /24
        self.sub_pub2 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ2_CIDR)

        switch_availability_zone(2)
        # TODO Change PUBLIC_SUBNET_AZ3_CIDR to subnet generator /24
        self.sub_pub3 = add_subnet(self, self.vpc, "subnet", PUBLIC_SUBNET_AZ3_CIDR)

        switch_availability_zone(0)
        # TODO Change PUBLIC_SUBNET_AZ1_CIDR to subnet generator /24
        self.sub_pri1 = add_subnet(self, self.vpc, "subnet", PRIVATE_SUBNET_AZ1_CIDR)

        switch_availability_zone(1)
        # TODO Change PUBLIC_SUBNET_AZ2_CIDR to subnet generator /24
        self.sub_pri2 = add_subnet(self, self.vpc, "subnet", PRIVATE_SUBNET_AZ2_CIDR)

        switch_availability_zone(2)
        # TODO Change PUBLIC_SUBNET_AZ3_CIDR to subnet generator /24
        self.sub_pri3 = add_subnet(self, self.vpc, "subnet", PRIVATE_SUBNET_AZ3_CIDR)

        # TODO Internet Gateway Class
        # TODO Internet Gateway Tests: Connect from instance to internet site
        self.internet_gateway = add_internet_gateway(self)
        self.internet_gateway_attachment = add_internet_gateway_attachment(self, self.vpc, self.internet_gateway)

        # TODO NAT
        # TODO NAT Security Group
        # TODO NAT Security Group Tests:
        self.nat_sg = add_security_group(self, self.vpc)
        self.nat = add_nat(self, self.sub_pub1, keypair_nat, self.nat_sg)

        # TODO Routing Tables
        # TODO Routing Tables Tests:
        self.public_route_table = add_route_table(self, self.vpc, route_type="Public")
        add_route_table_subnet_association(self, self.public_route_table, self.sub_pub1)
        add_route_table_subnet_association(self, self.public_route_table, self.sub_pub2)
        add_route_table_subnet_association(self, self.public_route_table, self.sub_pub3)
        add_route_ingress_via_gateway(self, self.public_route_table, self.internet_gateway, PUBLIC_CIDR)

        self.private_route_table = add_route_table(self, self.vpc, route_type="Private")
        add_route_table_subnet_association(self, self.public_route_table, self.sub_pri1)
        add_route_table_subnet_association(self, self.public_route_table, self.sub_pri2)
        add_route_table_subnet_association(self, self.public_route_table, self.sub_pri3)
        add_route_egress_via_NAT(self, self.private_route_table, self.nat)

        # TODO Jump Host Class
        # TODO Jump Host Security Group
        # TODO Tests: Connect from jumphost to subpub1 instance, subpub2 instance, cannot connect on port 80, 8080, 443,
        # TODO Tests: Try connecting to host in another vpc
        self.jump_sg = add_security_group(self, self.vpc)
        self.jumphost1 = add_nat(self, self.sub_pub1, keypair_jump, self.jump_sg)
        add_security_group_ingress(self, self.jump_sg, 'tcp', '22', '22', cidr=PUBLIC_COMPANY_CIDR)  # enable inbound SSH  access to the NAT from GA
        add_security_group_egress(self, self.jump_sg, 'tcp', '22', '22', cidr=VPC_CIDR)  # enable outbound SSH  access from the NAT to VPC






