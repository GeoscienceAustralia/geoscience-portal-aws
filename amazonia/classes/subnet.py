#!/usr/bin/python3
from troposphere import ec2, Tags, Ref, Join


class Subnet(object):
    def __init__(self, **kwargs):
        """
        Class to create subnets and associate a route table to it
        AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param stack: Stack template object
        :param route_table: Public or private route table object from stack
        :param az: Availability zone where the subnet will be deployed
        """
        super(Subnet, self).__init__()

        stack = kwargs['stack']
        pub_or_pri = 'Public' if kwargs['route_table'] == stack.pub_route_table else 'Private'

        """ Create Subnet
        """
        subnet_title = '{0}Subnet{1}'.format(pub_or_pri,
                                             kwargs['az'][-1:].upper())
        self.subnet = stack.add_resource(ec2.Subnet(subnet_title,
                                                    AvailabilityZone=kwargs['az'],
                                                    VpcId=Ref(stack.vpc),
                                                    CidrBlock=self.sub_cidr(stack,
                                                                            pub_or_pri),
                                                    Tags=Tags(Name=Join("",
                                                                        [Ref('AWS::StackName'),
                                                                         '-',
                                                                         subnet_title]))))

        """ Create Route Table Associations
        """
        self.rt_association = self.add_associate_route_table(stack, self.subnet, kwargs['route_table'])

    @staticmethod
    def sub_cidr(stack, pub_or_pri):
        """
        Function to help create Class C subnet CIDRs from Class A VPC CIDRs
        :param stack: Stack template object
        :param pub_or_pri: boolean for public or private subnet determined by route table
        :return: Subnet CIDR based on Public or Private and previous subnets created e.g. 10.1.2.0/24 or 10.0.1.0/24
        """
        # 3rd Octect: Obtain length of pub or pri subnet list
        octect_3 = len(stack.pub_sub_list) if pub_or_pri == 'Public' else len(stack.pri_sub_list)
        # 2nd Octect: set to '0' for public subnets, set to '1' for private subnets
        octect_2 = '0' if pub_or_pri == 'Public' else '1'
        vpc_split = stack.vpc.CidrBlock.split('.')      # separate VPC CIDR for renaming
        vpc_split[1] = octect_2                         # Set 2nd octect based on length of subnet list
        vpc_split[2] = str(octect_3)                    # set 3rd octect based on public or private
        vpc_last = vpc_split[3].split('/')              # split last group to change subnet mask
        vpc_last[1] = '24'                              # set subnet mask
        vpc_split[3] = '/'.join(vpc_last)               # join last group for subnet mask

        return '.'.join(vpc_split)

    @staticmethod
    def add_associate_route_table(stack, subnet, route_table):
        """
        Function to create a route table association
        AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        """

        route_table_ass = stack.add_resource(ec2.SubnetRouteTableAssociation(route_table.title + 'Association',
                                                                             RouteTableId=Ref(route_table),
                                                                             SubnetId=Ref(subnet)))
        return route_table_ass


