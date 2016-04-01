#!/usr/bin/python3
from troposphere import ec2, Tags, Ref, Join


class Subnet(object):
    def __init__(self, **kwargs):
        """
        Class to Create subnets route tables and assiociate the two
        AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param az - Availability Zone
        """
        super(Subnet, self).__init__()
        vpc = kwargs['vpc']
        stack = kwargs['stack']

        sub_num = self.num(kwargs['cidr'])
        subnet_title = 'subnet{0}'.format(sub_num + 1)
        self.subnet = stack.add_resource(ec2.Subnet(subnet_title,
                                                    AvailabilityZone=kwargs['az'],
                                                    VpcId=kwargs['vpc'],
                                                    CidrBlock=self.sub_cidr(kwargs['vpc'].CidrBlock,
                                                                            kwargs['route_table'].title),
                                                    Tags=Tags(Name=Join("",
                                                                        [Ref('AWS::StackName'),
                                                                         '-', subnet_title]))))

        """ Create route table associations
        """
        self.add_associate_route_table(stack, self.subnet, kwargs['route_table'])

    @staticmethod
    def num(cidr):
        """ Function to extract the 3rd octet from the Subnet cidr to determine availability zone and name subnets
        """
        cidr_split = cidr.split('.')

        return cidr_split[2]

    @staticmethod
    def sub_cidr(vpc_cidr, route_table_title):
        """
        Function to help create Class C subnet CIDRs from Class A VPC CIDRs
        :param vpc_cidr: VPC CIDR to be broken down into subnets e.g. 10.0.0.0/8
        :param num: Number of the Subnet
        :return:
        """
        # TODO test Subnet CIDR returns correctly from vpc CIDR fo rmultiple subnets
        vpc_split = vpc_cidr.split('.')
        vpc_split[2] = num
        vpc_last = vpc_split[3].split('/')
        vpc_last[1] = '24'
        vpc_split[3] = '/'.join(vpc_last)

        return '.'.join(vpc_split)

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


