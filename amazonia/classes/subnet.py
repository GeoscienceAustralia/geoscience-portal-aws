#!/usr/bin/python3

from amazonia.amazonia.amazonia_resources import *



class Subnet(object):
    def __init__(self, **kwargs):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(object, self).__init__(**kwargs)
        num = num(cidr)
        switch_availability_zone(0)

        subnet = template.add_resource(ec2.Subnet(subnet_title,
                                                  AvailabilityZone=AVAILABILITY_ZONES[current_az],
                                                  VpcId=isCfObject(vpc),
                                                  CidrBlock=cidr,
                                                  Tags=Tags(Name=name_tag(subnet_title),
                                                            Environment=ENVIRONMENT_NAME)))

        add_route_table_subnet_association(self, self.public_route_table, subnet)

    def num(self, cidr):
        cidr_split = self.cidr.split('.')

        return cidr_split[2]

        # TODO Routing Tables Class
        # TODO Routing Tables Unit Tests:
    def route_table(self):
        self.public_route_table = add_route_table(self, self.vpc, route_type="Public")

    def associate_route_table(self):

        add_route_table_subnet_association(self, self.public_route_table, sub_pub2)
        add_route_table_subnet_association(self, self.public_route_table, sub_pub3)


        self.private_route_table = add_route_table(self, self.vpc, route_type="Private")
        add_route_table_subnet_association(self, self.public_route_table, sub_pri1)
        add_route_table_subnet_association(self, self.public_route_table, sub_pri2)
        add_route_table_subnet_association(self, self.public_route_table, sub_pri3)


