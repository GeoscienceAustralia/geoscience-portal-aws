# pylint: disable=too-many-arguments, line-too-long

from amazonia.amazonia_resources import *
from troposphere import Template
from amazonia.classes.subnet import Subnet
from amazonia.classes.single_instance import SingleInstance


class Stack(Template):
    def __init__(self, invpc="", keypair_nat="", keypair_jump=""):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(Stack, self).__init__()

        vpc_cidr = VPC_CIDR   # TODO Change VPC_CIDR to CIDR generator

        if invpc == "":
            self.vpc = add_vpc(self, vpc_cidr)
        else:
            self.vpc = invpc

        # TODO Internet Gateway Class
        # TODO Internet Gateway Unit Tests: validate that internet_gateway=internet_gateway_attachment.InternetGatewayId
        # TODO Internet Gateway Sys Tests: Connect from instance to internet site
        self.internet_gateway = add_internet_gateway(self)
        self.internet_gateway_attachment = add_internet_gateway_attachment(self, self.vpc, self.internet_gateway)

        # TODO possible enumeration?
        sub_pub1 = Subnet(stack=self, internet_gateway=self.internet_gateway, cidr=self.cidr_mgt(vpc_cidr, 0))
        sub_pub2 = Subnet(stack=self, internet_gateway=self.internet_gateway, cidr=self.cidr_mgt(vpc_cidr, 1))
        sub_pub3 = Subnet(stack=self, internet_gateway=self.internet_gateway, cidr=self.cidr_mgt(vpc_cidr, 2))

        self.nat = SingleInstance(stack=self, subnet=sub_pub1, keypair=keypair_nat)
        self.jump = SingleInstance(stack=self, subnet=sub_pub1, keypair=keypair_jump)

        sub_pri1 = Subnet(stack=self, nat=self.nat, cidr=self.cidr_mgt(vpc_cidr, 3))
        sub_pri2 = Subnet(stack=self, nat=self.nat, cidr=self.cidr_mgt(vpc_cidr, 4))
        sub_pri3 = Subnet(stack=self, nat=self.nat, cidr=self.cidr_mgt(vpc_cidr, 5))

        unit()
            self.database = database(stack=self, **kwargs) if database={database}

    def cidr_mgt(self, vpc_cidr, num):
        """

        :param vpc_cidr:
        :param num:
        :return:
        """
        # TODO test Subnet CIDR returns correctly from vpc CIDR fo rmultiple subnets
        vpc_split = vpc_cidr.split('.')
        vpc_split[2] = num
        vpc_last = vpc_split[3].split('/')
        vpc_last[1] = '24'
        vpc_split[3] = '/'.join(vpc_last)

        return '.'.join(vpc_split)