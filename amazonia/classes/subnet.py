#!/usr/bin/python3
from troposphere import ec2, Tags, Ref, Join


class Subnet(object):
    def __init__(self, **kwargs):
        """
        Class to Create subnets route tables and assiociate the two
        AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        """
        super(Subnet, self).__init__()
        vpc = kwargs['vpc']
        stack = kwargs['stack']

        sub_num = self.num(kwargs['cidr'])
        subnet_title = 'subnet{0}'.format(sub_num + 1)
        self.subnet = stack.add_resource(ec2.Subnet(subnet_title,
                                                    AvailabilityZone=self.availability_zone(sub_num),
                                                    VpcId=kwargs['vpc'],
                                                    CidrBlock=kwargs['cidr'],
                                                    Tags=Tags(Name=Join("",
                                                                        [Ref('AWS::StackName'),
                                                                         '-', subnet_title]))))

        """ Create route table and associations
        """
        if not kwargs['route_table']:
            self.route_table = self.add_route_table(vpc=vpc)
            self.add_associate_route_table(stack, self.subnet, self.route_table)
        else:
            self.add_associate_route_table(stack, self.subnet, kwargs['route_table'])

    @staticmethod
    def num(cidr):
        """ Function to extract the 3rd octect from the SUbnet cidr to determine availability zone and name subnets
        """
        cidr_split = cidr.split('.')

        return cidr_split[2]



    @staticmethod
    def add_associate_route_table(stack, subnet, route_table):
        """
        Function to create a route toable association with a subnet and add it to the stack template
        AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        """

        route_table_ass = stack.add_resource(ec2.SubnetRouteTableAssociation(route_table.title + 'Association',
                                                                             RouteTableId=Ref(route_table),
                                                                             SubnetId=Ref(subnet)))
        return route_table_ass

    @staticmethod
    def availability_zone(sub_num):
        """ Function to return the current availability zone id based on the subnet cidr
        """
        az_alpha = {'0': 'a', '1': 'b', '2': 'c'}
        return 'ap-southeast-2{0}'.format(az_alpha[sub_num])
