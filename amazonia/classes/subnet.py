#!/usr/bin/python3
from troposphere import ec2, Tags


class Subnet(object):
    def __init__(self, **kwargs):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(object, self).__init__(**kwargs)
        subnum = self.num(kwargs['cidr'])
        switch_availability_zone(subnum)

        subnet = template.add_resource(ec2.Subnet(subnet_title + subnum,
                                                  AvailabilityZone=AVAILABILITY_ZONES[current_az],
                                                  VpcId=kwargs['vpc'],
                                                  CidrBlock=kwargs['cidr'],
                                                  Tags=Tags(Name=name_tag(subnet_title))))

        # Route Table
        if not kwargs['route_table']:
            route_table = route_table()

        # Route Table Association
            route_table_asosciation = associate_route_table()

    def num(self, cidr):
        cidr_split = self.cidr.split('.')

        return cidr_split[2]


        # TODO Routing Tables Unit Tests:

    def route_table(self):
        route_table = template.add_resource(ec2.RouteTable(rt_title,
                                                           VpcId=kwargs['vpc'],
                                                           Tags=Tags(Name=rt_title)))
        return route_table

    def associate_route_table(self):
        template.add_resource(ec2.SubnetRouteTableAssociation(rt_title + association,
                                                              RouteTableId=Ref(route_table),
                                                              SubnetId=Ref(subnet)))




