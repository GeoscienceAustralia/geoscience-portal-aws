#!/usr/bin/python3

from troposphere import Template, ec2, Tags
from amazonia.classes.subnet import Subnet
from amazonia.classes.single_instance import SingleInstance


class Stack(Template):
    def __init__(self, invpc="", keypair_nat="", keypair_jump=""):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(Stack, self).__init__()

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
        public_route_table = self.add_resource(ec2.RouteTable('PublicRouteTable',
                                                              VpcId=self.vpc,
                                                              Tags=Tags(Name='PublicRouteTable')))

        private_route_table = self.add_resource(ec2.RouteTable('PrivateRouteTable',
                                                               VpcId=self.vpc,
                                                               Tags=Tags(Name='PrivateRouteTable')))

        """ Create Private Subnets
        """
        az = len(availability_zones)
        self.pub_sub_list = []
        for sub_num in range(0, az):
            if sub_num == 0:  # create route table in first loop
                self.pub_sub_list.append(Subnet(stack=self,
                                                internet_gateway=self.internet_gateway,
                                                cidr=self.cidr_mgt(vpc_cidr, sub_num)))
            else:  # uses route table created in first loop
                self.pub_sub_list.append(Subnet(stack=self,
                                                internet_gateway=self.internet_gateway,
                                                route_table=self.pub_sub_list[0].route_table,
                                                cidr=self.cidr_mgt(vpc_cidr, sub_num)))

        # TODO Rewrite -add_route_ingress_via_gateway(self, self.public_route_table, self.internet_gateway, PUBLIC_CIDR)

        """ Create NAT and Jumpbox
        """
        self.nat = SingleInstance(stack=self, subnet=self.pub_sub_list[0], keypair=keypair_nat)
        self.jump = SingleInstance(stack=self, subnet=self.pub_sub_list[0], keypair=keypair_jump)

        """ Create Private Subnets
        """
        self.pri_sub_list = []
        for sub_num in range(az, 2*az):
            if sub_num == 0:  # create route table in first loop
                self.pri_sub_list.append(Subnet(stack=self,
                                                nat=self.nat,
                                                cidr=self.cidr_mgt(vpc_cidr, sub_num)))
            else:  # uses route table created in first loop
                self.pri_sub_list.append(Subnet(stack=self,
                                                route_table=self.pri_sub_list[0].route_table,
                                                nat=self.nat,
                                                cidr=self.cidr_mgt(vpc_cidr, sub_num)))

        # TODO Rewrite - add_route_egress_via_NAT(stack, self.private_route_table, self.nat)

        """ Create Unit
        """
        # read in yaml['units']
        for unit in units:
            Unit(**kwargs)

    @staticmethod
    def cidr_mgt(vpc_cidr, num):
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
