#!/usr/bin/python3
from troposphere import ec2, Tags, Ref, Join


class Subnet(object):
    def __init__(self, **kwargs):
        """
        Class to create subnets and associate a route table to it
        AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param stack: Stack template object with required:
                      * VPC w/ CIDR block,
                      * Public and private route tables,
                      * Initialised public and private subnet lists
        :param route_table: Public or private route table object from stack
        :param az: Availability zone where the subnet will be deployed
        """
        super(Subnet, self).__init__()

        self.template = kwargs['template']
        self.cidr = kwargs['cidr']
        self.vpc = kwargs['vpc']
        self.pub_or_pri = 'Public' if kwargs['is_public'] else 'Private'

        """ Create Subnet
        """
        subnet_title = self.pub_or_pri + 'Subnet' + kwargs['az'][-1:].upper()
        self.subnet = self.template.add_resource(ec2.Subnet(subnet_title,
                                                            AvailabilityZone=kwargs['az'],
                                                            VpcId=Ref(self.vpc),
                                                            CidrBlock=self.cidr,
                                                            Tags=Tags(Name=Join("",
                                                                                [Ref('AWS::StackName'),
                                                                                 '-',
                                                                                 subnet_title]))))

        """ Create Route Table Associations
        """
        self.rt_association = self.add_associate_route_table(kwargs['route_table'])

    def add_associate_route_table(self, route_table):
        """
        Function to create a route table association
        AWS CloudFormation -
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        """

        route_table_ass = self.template.add_resource(ec2.SubnetRouteTableAssociation(route_table.title +
                                                                                     self.subnet.title +
                                                                                     'Association',
                                                                                     RouteTableId=Ref(route_table),
                                                                                     SubnetId=Ref(self.subnet)))
        return route_table_ass
