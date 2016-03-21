# pylint: disable=too-many-arguments, line-too-long

from amazonia.amazonia_resources import *
from troposphere import Template


class Subnet(object):
    def __init__(self, **kwargs):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(object, self).__init__()
        num = num(cidr)
        switch_availability_zone(0)
        # TODO Change PUBLIC_SUBNET_AZ1_CIDR to subnet generator /24
        sub_pub1 = add_subnet(self, self.vpc, "subnet", cidr)

    def num(self, cidr):
        cidr_split = self.cidr.split('.')

        return cidr_split[2]

        # TODO Routing Tables Class
        # TODO Routing Tables Unit Tests:
        self.public_route_table = add_route_table(self, self.vpc, route_type="Public")
        add_route_table_subnet_association(self, self.public_route_table, sub_pub1)
        add_route_table_subnet_association(self, self.public_route_table, sub_pub2)
        add_route_table_subnet_association(self, self.public_route_table, sub_pub3)
        add_route_ingress_via_gateway(self, self.public_route_table, self.internet_gateway, PUBLIC_CIDR)

        self.private_route_table = add_route_table(self, self.vpc, route_type="Private")
        add_route_table_subnet_association(self, self.public_route_table, sub_pri1)
        add_route_table_subnet_association(self, self.public_route_table, sub_pri2)
        add_route_table_subnet_association(self, self.public_route_table, sub_pri3)
        add_route_egress_via_NAT(stack, self.private_route_table, self.nat)

