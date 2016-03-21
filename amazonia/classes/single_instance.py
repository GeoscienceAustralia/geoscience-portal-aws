# pylint: disable=too-many-arguments, line-too-long

from amazonia.amazonia_resources import *


class SingleInstance(object):
    def __init__(self, **kwargs):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(object, self).__init__()

        self.sg = add_security_group(self, self.vpc)
        self.single = add_nat(self, subnet, keypair, self.sg)

        # TODO NAT Security Group Unit Tests: validate that nat_sg = nat.NetworkInterfaces.GroupSet
        # TODO Unit Tests:jump_sg = jumphost1.NetworkInterfaces.GroupSet,
        # TODO Sys Tests: Connect from jumphost to subpub1 instance, subpub2 instance, can't connect on port 80,8080,443
        # TODO Sys Tests: Try connecting to host in another vpc

        # TODO update the 3 below rules to refer to a security group within private subnets instead (once we have some)
        add_security_group_ingress(self, self.nat_sg, '-1', '-1', '-1', cidr=PRIVATE_SUBNET_AZ1_CIDR)
        add_security_group_ingress(self, self.nat_sg, '-1', '-1', '-1', cidr=PRIVATE_SUBNET_AZ2_CIDR)
        add_security_group_ingress(self, self.nat_sg, '-1', '-1', '-1', cidr=PRIVATE_SUBNET_AZ3_CIDR)
        add_security_group_egress(self, self.nat_sg, '-1', '-1', '-1', cidr=PUBLIC_CIDR)

        add_security_group_ingress(self, self.jump_sg, 'tcp', '22', '22', cidr=PUBLIC_COMPANY_CIDR) # enable inbound SSH  access to the NAT from GA
        add_security_group_egress(self, self.jump_sg, 'tcp', '22', '22', cidr=VPC_CIDR) # enable outbound SSH  access from the NAT to VPC