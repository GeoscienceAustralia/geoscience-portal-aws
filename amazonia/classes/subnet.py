#!/usr/bin/python3
from troposphere import ec2

class Subnet(object):
    def __init__(self, **kwargs):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(object, self).__init__(**kwargs)
        subnum = self.num(kwargs['cidr'])
        switch_availability_zone(subnum)

        subnet = template.add_resource(ec2.Subnet(subnet_title + subnum,
                                                  AvailabilityZone= TODO AVAILABILITY_ZONES[current_az],
                                                  VpcId=kwargs['vpc'],
                                                  CidrBlock=kwargs['cidr'],
                                                  Tags=Tags(Name=name_tag(subnet_title),
                                                            Environment=ENVIRONMENT_NAME)))

        add_route_table_subnet_association(self, self.public_route_table, subnet)

        return subnet
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


