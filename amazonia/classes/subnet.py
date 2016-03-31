#!/usr/bin/python3
from troposphere import ec2, Tags, Ref, Join


class Subnet(object):
    def __init__(self, **kwargs):
        """ Class to Create subnets and assiociate  """
        super(object, self).__init__(stack=kwargs['stack'])

        sub_num = self.num(kwargs['cidr'])
        subnet_title = 'subnet{0}'.format(sub_num + 1)
        subnet = template.add_resource(ec2.Subnet(subnet_title,
                                                  AvailabilityZone=self.availability_zone(sub_num),
                                                  VpcId=kwargs['vpc'],
                                                  CidrBlock=kwargs['cidr'],
                                                  Tags=Tags(Name=Join("", [Ref('AWS::StackName'), '-', subnet_title]))))

        # Route Table
        if not kwargs['route_table']:
            route_table = route_table()

        # Route Table Association
            route_table_asosciation = associate_route_table()

    def num(self, cidr):
        cidr_split = cidr.split('.')

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

    @staticmethod
    def availability_zone(sub_num):
        """ Function to return the current Availability Zone Id based on the subnet cidr
        """
        az_alpha = {'0': 'a', '1': 'b', '2': 'c'}
        return 'ap-southeast-2{0}'.format(az_alpha[sub_num])
