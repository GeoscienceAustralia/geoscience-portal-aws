#!/usr/bin/python3

from troposphere import Template, ec2

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.subnet import Subnet
from amazonia.classes.unit import Unit


class Stack(Template):
    def __init__(self, **kwargs):
        super(Stack, self).__init__()
        self.title = kwargs['title']
        self.internet_gateway = self.gateway_attachment = None
        self.nat = self.jump = None
        self.units = []
        self.private_subnets = self.public_subnets = []
        self.pub_route_table = self.pri_route_table = None
        self.availability_zones = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']  # TODO read in AZ list from yaml
        self.vpc = self.add_resource(ec2.VPC(self.title + "Vpc", CidrBlock='10.0.0.0/24')) # TODO Change VPC_CIDR to CIDR generator
        self.create_internet_gateway()
        self.create_route_tables()
        self.create_subnets()

        # TODO Rewrite -add_route_ingress_via_gateway(self, self.public_route_table, self.internet_gateway, PUBLIC_CIDR)

        self.jump = SingleInstance(
            title=kwargs['title'] + 'jump',
            keypair=kwargs['keypair'],
            si_image_id=kwargs['image_id'],
            si_instance_type=kwargs['instance_type'],
            subnet=self.public_subnets[0],
            vpc=self.vpc,
            stack=self
        )

        self.nat = SingleInstance(
            title=kwargs['title'] + 'nat',
            keypair=kwargs['keypair'],
            si_image_id=kwargs['nat_image_id'],
            si_instance_type=kwargs['instance_type'],
            subnet=self.public_subnets[0],
            vpc=self.vpc,
            stack=self
        )

        # TODO Rewrite - add_route_egress_via_NAT(stack, self.private_route_table, self.nat)

        """ Create Unit
        """
        # read in yaml['units']
        for unit in units:
            self.units.append(Unit(title=kwargs['title'],
                                   vpc=self.vpc,
                                   stack=self,
                                   protocol=kwargs['protocol'],
                                   port=kwargs['port'],
                                   path2ping=kwargs['path2ping'],
                                   public_subnets=self.public_subnets,
                                   private_subnets=self.private_subnets,
                                   minsize=kwargs['minsize'],
                                   maxsize=kwargs['maxsize'],
                                   keypair=kwargs['keypair'],
                                   image_id=kwargs['image_id'],
                                   instance_type=kwargs['instance_type'],
                                   userdata=kwargs['userdata'],
                                   service_role_arn=kwargs['code_deploy_service_role'],
                                   nat=self.nat,
                                   jump=self.jump,
                                   ))

    def get_route_table(self, sub_list):  # TODO Write unit test for get_route_table
        if sub_list == self.public_subnets:
            return self.pub_route_table
        else:
            return self.pri_route_table

    def create_internet_gateway(self):
        self.internet_gateway = self.add_resource(ec2.InternetGateway(self.title + "Ig"))
        self.gateway_attachment = self.add_resource(ec2.VPCGatewayAttachment(self.internet_gateway.title + "Atch",
                                                                             VpcId=self.vpc,
                                                                             InternetGatewayId=self.internet_gateway))

    def create_route_tables(self):
        """
            Create Route Tables
            AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html
            Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
            """
        self.pub_route_table = self.add_resource(ec2.RouteTable(self.title + 'PubRt',
                                                                VpcId=self.vpc))

        self.pri_route_table = self.add_resource(ec2.RouteTable(self.title + 'PriRt',
                                                                VpcId=self.vpc))

    def create_subnets(self):
        """ Create Subnets
        """
        all_subnets = [self.private_subnets, self.public_subnets]
        for sub_list in all_subnets:
            for az in self.availability_zones:
                sub_list.append(Subnet(stack=self,
                                       internet_gateway=self.internet_gateway,
                                       route_table=self.get_route_table(sub_list),
                                       availability_zone=az,
                                       cidr=self.vpc.CidrBlock))
