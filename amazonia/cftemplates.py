# pylint: disable=too-many-arguments

""" Templates to implement common cloud formation configurations

The functions in this module generate cloud formation scripts that install common AWS environments and components

"""

from amazonia_resources import *


def addVPC(template):
    """Create a VPC resource and add it to the given template."""
    vpc = add_vpc(template, VPC_CIDR)  
    return vpc


def addSingleAZenv(template, vpc, key_pair_name):
    """ Public function to create a single AZ environment in a vpc """

    # configure network
    public_subnet = add_subnet(template, vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
    public_route_table = add_route_table(template, vpc, public_subnet, "Public")
    internet_gateway = add_internet_gateway(template, vpc)
    add_route_ingress_via_gateway(template, public_route_table, internet_gateway, PUBLIC_CIDR)
    private_subnet = add_subnet(template, vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ1_CIDR)
    private_route_table = add_route_table(template, vpc, private_subnet, "Private")
    nat = add_nat(template, public_subnet, key_pair_name)
    nat_sg = add_security_group(template, vpc, [nat])
    add_route_egress_via_NAT(template, private_route_table, nat)
    # enable inbound http access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'tcp', '80', '80', PUBLIC_CIDR)
    # enable inbound https access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'tcp', '443', '443', PUBLIC_CIDR)
    # enable inbound SSH  access to the NAT from GA
    add_security_group_ingress(template, nat_sg, 'tcp', '22', '22', PUBLIC_GA_GOV_AU_CIDR)
    # enable inbound ICMP access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'icmp', '-1', '-1', PUBLIC_CIDR)

    return template

def addDualAZenv(template, vpc, key_pair_name):
    """ Public function to create a dual AZ environment in a vpc """

    # AZ 1
    public_subnet1 = add_subnet(template, vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
    public_route_table = add_route_table(template, vpc, public_subnet1, "Public")
    internet_gateway = add_internet_gateway(template, vpc)
    add_route_ingress_via_gateway(template, public_route_table, internet_gateway, PUBLIC_CIDR)
    private_subnet = add_subnet(template, vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ1_CIDR)
    private_route_table = add_route_table(template, vpc, private_subnet, "Private")
    nat = add_nat(template, public_subnet1, key_pair_name)
    nat_sg = add_security_group(template, vpc, [nat])
    add_route_egress_via_NAT(template, private_route_table, nat)
    # enable inbound http access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'tcp', '80', '80', PUBLIC_CIDR)
    # enable inbound https access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'tcp', '443', '443', PUBLIC_CIDR)
    # enable inbound SSH  access to the NAT from GA
    add_security_group_ingress(template, nat_sg, 'tcp', '22', '22', PUBLIC_GA_GOV_AU_CIDR)
    # enable inbound ICMP access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'icmp', '-1', '-1', PUBLIC_CIDR)

    switch_availability_zone()

    # AZ 2
    public_subnet2 = add_subnet(template, vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ2_CIDR)
    private_subnet = add_subnet(template, vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ2_CIDR)
    private_route_table = add_route_table(template, vpc, private_subnet, "Private")
    nat = add_nat(template, public_subnet2, key_pair_name)
    add_route_egress_via_NAT(template, private_route_table, nat)
    # enable inbound http access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'tcp', '80', '80', PUBLIC_CIDR)
    # enable inbound https access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'tcp', '443', '443', PUBLIC_CIDR)
    # enable inbound SSH  access to the NAT from GA
    add_security_group_ingress(template, nat_sg, 'tcp', '22', '22', PUBLIC_GA_GOV_AU_CIDR)
    # enable inbound ICMP access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'icmp', '-1', '-1', PUBLIC_CIDR)

    #WEB INSTANCES
    userdata="#!/bin/sh\nyum -y install httpd && chkconfig httpd on && /etc/init.d/httpd start"

    web_instance1 = add_web_instance(template, "", public_subnet1, userdata)
    web_instance2 = add_web_instance(template, "", public_subnet2, userdata)

    #Web Security Group
    web_sg = add_security_group(template, vpc, [web_instance1, web_instance2])
    add_security_group_ingress(template, web_sg, 'tcp', '80', '80', PUBLIC_CIDR)
    add_security_group_ingress(template, web_sg, 'tcp', '443', '443', PUBLIC_CIDR)
    add_security_group_ingress(template, web_sg, 'tcp', '22', '22', PUBLIC_GA_GOV_AU_CIDR)

    add_load_balancer(template, [web_instance1.title, web_instance2.title], [public_subnet1.title, public_subnet2.title], "HTTP:80/elbtest.html", web_sg)

    return template