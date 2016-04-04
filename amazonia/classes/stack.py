#!/usr/bin/python3

from troposphere import Template, ec2, Tags
from amazonia.classes.subnet import Subnet
from amazonia.classes.single_instance import SingleInstance


class Stack(Template):
    def __init__(self, invpc='', keypair_nat='', keypair_jump='', title=''):  # TODO confirm kwargs to be passed in
        """ Public Class to create a Triple AZ environment in a vpc """
        super(Stack, self).__init__()
        self.title = title  # title of unit
        vpc_cidr = '10.0.0.0/24'   # TODO Change VPC_CIDR to CIDR generator
        availability_zones = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']  # TODO read in AZ list from yaml

        if invpc == "":
            self.vpc = add_vpc(self, vpc_cidr)
        else:
            self.vpc = invpc

        """
        Create Internet Gateway
        AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internet-gateway.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        """
        # TODO Internet Gateway Unit Tests: validate that internet_gateway=internet_gateway_attachment.InternetGatewayId
        # TODO Internet Gateway Sys Tests: Connect from instance to internet site
        self.internet_gateway = add_internet_gateway(self)  # TODO rewrite internetgateway
        self.internet_gateway_attachment = add_internet_gateway_attachment(self, self.vpc, self.internet_gateway)

        """
        Create Route Tables
        AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        """
        self.pub_route_table = self.add_resource(ec2.RouteTable('{0}PublicRouteTable'.format(self.title),
                                                                VpcId=self.vpc,
                                                                Tags=Tags(
                                                                    Name='{0}PublicRouteTable'.format(self.title))))

        self.pri_route_table = self.add_resource(ec2.RouteTable('{0}PrivateRouteTable'.format(self.title),
                                                                VpcId=self.vpc,
                                                                Tags=Tags(
                                                                    Name='{0}PrivateRouteTable'.format(self.title)
                                                                )))

        """ Create Subnets
        """

        self.pri_sub_list = []
        self.pub_sub_list = []
        pub_pri_sub_lists = [self.pri_sub_list, self.pub_sub_list]

        for sub_list in pub_pri_sub_lists:
            for az in availability_zones:
                sub_list.append(Subnet(stack=self,
                                       internet_gateway=self.internet_gateway,
                                       route_table=self.get_route_table(sub_list),
                                       availability_zone=az,
                                       cidr=vpc_cidr))

        # TODO Rewrite -add_route_ingress_via_gateway(self, self.public_route_table, self.internet_gateway, PUBLIC_CIDR)

        """ Create NAT and Jumpbox
        """
        self.nat = SingleInstance(stack=self, subnet=self.pub_sub_list[0], keypair=keypair_nat)
        self.jump = SingleInstance(stack=self, subnet=self.pub_sub_list[0], keypair=keypair_jump)

        """ Create Private Subnets
        """

        for sub_num in range(az, 2*az):
                self.pri_sub_list.append(Subnet(stack=self,
                                                route_table=self.private_route_table,
                                                nat=self.nat,
                                                cidr=self.cidr_mgt(vpc_cidr, sub_num)))

        # TODO Rewrite - add_route_egress_via_NAT(stack, self.private_route_table, self.nat)

        """ Create Unit
        """
        # read in yaml['units']
        for unit in units:
            Unit(**kwargs)

    def get_route_table(self, sub_list):  # TODO Write unit test for get_route_table
        if sub_list == self.pub_sub_list:
            return self.pub_route_table
        else:
            return self.pri_route_table
