#!/usr/bin/python3
from troposphere import ec2, Tags, Ref, Join


class Subnet(object):
    def __init__(self, **kwargs):
        """
        Class to Create subnets route tables and assiociate the two
        AWS CLoudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        """
        super(Subnet, self).__init__()
        vpc = kwargs['vpc']
        stack = kwargs['stack']
        sub_num = self.num(kwargs['cidr'])
        subnet_title = 'subnet{0}'.format(sub_num + 1)
        subnet = stack.add_resource(ec2.Subnet(subnet_title,
                                               AvailabilityZone=self.availability_zone(sub_num),
                                               VpcId=kwargs['vpc'],
                                               CidrBlock=kwargs['cidr'],
                                               Tags=Tags(Name=Join("",
                                                                   [Ref('AWS::StackName'),
                                                                    '-', subnet_title]))))

        # Route Table
        if not kwargs['route_table']:
            route_table = self.route_table(vpc=vpc)
            self.associate_route_table(route_table)
        else:
            self.associate_route_table(kwargs['route_table'])

    @staticmethod
    def num(cidr):
        cidr_split = cidr.split('.')

        return cidr_split[2]

    @staticmethod
    def route_table(self, **kwargs):

        rt_title = 'PublicRouteTable' if kwargs['internet_gateway'] else 'PrivateRouteTable'

        route_table = self.stack.add_resource(ec2.RouteTable(rt_title,
                                                             VpcId=kwargs['vpc'],
                                                             Tags=Tags(Name=rt_title)))
        return route_table

    @staticmethod
    def associate_route_table(self, route_table):

        route_table_ass = self.stack.add_resource(ec2.SubnetRouteTableAssociation(route_table.title + 'Association',
                                                                                  RouteTableId=Ref(route_table),
                                                                                  SubnetId=Ref(self.subnet)))
        return route_table_ass

    @staticmethod
    def availability_zone(sub_num):
        """ Function to return the current Availability Zone Id based on the subnet cidr
        """
        az_alpha = {'0': 'a', '1': 'b', '2': 'c'}
        return 'ap-southeast-2{0}'.format(az_alpha[sub_num])
