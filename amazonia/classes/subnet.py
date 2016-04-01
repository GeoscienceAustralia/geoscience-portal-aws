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

        stack = kwargs['stack']
        pub_or_pri = 'Public' if kwargs['route_table'] == stack.pub_route_table else 'Private'
        subnet_title = '{0}Subnet{1}'.format(pub_or_pri, kwargs['az'][-1:].upper())

        self.subnet = stack.add_resource(ec2.Subnet(subnet_title,
                                                    AvailabilityZone=kwargs['az'],
                                                    VpcId=kwargs['vpc'],
                                                    CidrBlock=self.sub_cidr(stack, kwargs['vpc'].CidrBlock,
                                                                            pub_or_pri),
                                                    Tags=Tags(Name=Join("",
                                                                        [Ref('AWS::StackName'),
                                                                         '-', subnet_title]))))

        """ Create route table associations
        """
        self.rt_association = self.add_associate_route_table(stack, self.subnet, kwargs['route_table'])

    @staticmethod
    def sub_cidr(stack, vpc_cidr, pub_or_pri):
        """
        Function to help create Class C subnet CIDRs from Class A VPC CIDRs
        :param stack: Stack template
        :param vpc_cidr: VPC CIDR to be broken down into subnets e.g. 10.0.0.0/8
        :param pub_or_pri: boolean for public or provate subnet determined by route table
        :return:
        """
        # 3rd Octect: Obtain length of pub or pri subnet list
        octect_3 = len(stack.pub_sub_list) if pub_or_pri == 'Public' else len(stack.pri_sub_list)
        # 2nd Octect: set to '0' for public subnets, set to '1' for private subnets
        octect_2 = '0' if pub_or_pri == 'Public' else '1'
        vpc_split = vpc_cidr.split('.')     # separate VPC CIDR for renaming
        vpc_split[1] = octect_2             # Set 2nd octect based on length of subnet list
        vpc_split[2] = octect_3             # set 3rd octect based on public or private
        vpc_last = vpc_split[3].split('/')  # split last group to change subnet mask
        vpc_last[1] = '24'                  # set subnet mask
        vpc_split[3] = '/'.join(vpc_last)   # join last group for subnet mask

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


