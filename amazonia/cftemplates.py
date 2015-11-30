# pylint: disable=too-many-arguments

""" Templates to implement common cloud formation configurations

The functions in this module generate cloud formation scripts that install common AWS environments and components

"""

from amazonia_resources import *
from troposphere import Template


def addVPC(template):
    """Create a VPC resource and add it to the given template."""
    vpc = add_vpc(template, VPC_CIDR)  
    return vpc

class SingleAZenv(Template):

   def __init__(self, key_pair_name):
    """ Public function to create a single AZ environment in a vpc """
    super(SingleAZenv,self).__init__()
    self.vpc = addVPC(self)

    # configure network
    self.public_subnet = add_subnet(self, self.vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
    public_route_table = add_route_table(self, self.vpc, "Public")
    add_route_table_subnet_association (self, public_route_table, self.public_subnet)

    internet_gateway = add_internet_gateway(self, self.vpc)
    add_route_ingress_via_gateway(self, public_route_table, internet_gateway, PUBLIC_CIDR)
    self.private_subnet = add_subnet(self, self.vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ1_CIDR)
    private_route_table = add_route_table(self, self.vpc, "Private")
    add_route_table_subnet_association (self, private_route_table, self.private_subnet)

    #NAT Security Group
    nat_sg = add_security_group(self, self.vpc)
    # enable inbound http access to the NAT from anywhere
    add_security_group_ingress(self, nat_sg, 'tcp', '80', '80', PUBLIC_CIDR)
    # enable inbound https access to the NAT from anywhere
    add_security_group_ingress(self, nat_sg, 'tcp', '443', '443', PUBLIC_CIDR)
    # enable inbound SSH  access to the NAT from GA
    add_security_group_ingress(self, nat_sg, 'tcp', '22', '22', PUBLIC_GA_GOV_AU_CIDR)
    # enable inbound ICMP access to the NAT from anywhere
    add_security_group_ingress(self, nat_sg, 'icmp', '-1', '-1', PUBLIC_CIDR)

    self.nat = add_nat(self, self.public_subnet, key_pair_name, nat_sg)
    add_route_egress_via_NAT(self, private_route_table, self.nat)

def addDualAZenv(template, vpc, key_pair_name):
    """ Public function to create a dual AZ environment in a vpc """

    # AZ 1
    public_subnet1 = add_subnet(template, vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
    public_route_table1 = add_route_table(template, vpc, "Public")
    add_route_table_subnet_association(template, public_route_table1, public_subnet1)
    internet_gateway = add_internet_gateway(template, vpc)
    add_route_ingress_via_gateway(template, public_route_table1, internet_gateway, PUBLIC_CIDR)
    private_subnet1 = add_subnet(template, vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ1_CIDR)
    private_route_table1 = add_route_table(template, vpc, "Private")
    add_route_table_subnet_association (template, private_route_table1, private_subnet1)

    
    #NAT Security Group
    nat_sg = add_security_group(template, vpc)
    # enable inbound http access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'tcp', '80', '80', PUBLIC_CIDR)
    # enable inbound https access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'tcp', '443', '443', PUBLIC_CIDR)
    # enable inbound SSH  access to the NAT from GA
    add_security_group_ingress(template, nat_sg, 'tcp', '22', '22', PUBLIC_GA_GOV_AU_CIDR)
    # enable inbound ICMP access to the NAT from anywhere
    add_security_group_ingress(template, nat_sg, 'icmp', '-1', '-1', PUBLIC_CIDR)

    nat = add_nat(template, public_subnet1, key_pair_name, nat_sg)
    add_route_egress_via_NAT(template, private_route_table1, nat)

    switch_availability_zone()

    # AZ 2
    public_subnet2 = add_subnet(template, vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ2_CIDR)
    # Note below how we associate public subnet 2 to the single public route table we create for the VPC
    add_route_table_subnet_association(template, public_route_table1, public_subnet2)
    
    private_subnet2 = add_subnet(template, vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ2_CIDR)
    private_route_table2 = add_route_table(template, vpc, "Private")
    add_route_table_subnet_association(template, private_route_table2, private_subnet2)
    
    nat = add_nat(template, public_subnet2, key_pair_name, nat_sg)
    add_route_egress_via_NAT(template, private_route_table2, nat)

    #Web Security Group
    web_sg = add_security_group(template, vpc)
    add_security_group_ingress(template, web_sg, 'tcp', '80', '80', PUBLIC_CIDR)
    add_security_group_ingress(template, web_sg, 'tcp', '443', '443', PUBLIC_CIDR)
    add_security_group_ingress(template, web_sg, 'tcp', '22', '22', PUBLIC_GA_GOV_AU_CIDR)

    web_instance1 = add_web_instance(template, key_pair_name, public_subnet1, web_sg, WEB_SERVER_AZ1_USER_DATA)
    web_instance2 = add_web_instance(template, key_pair_name, public_subnet2, web_sg, WEB_SERVER_AZ2_USER_DATA)

    add_load_balancer(template, [web_instance1.title, web_instance2.title], [public_subnet1.title, public_subnet2.title], "HTTP:80/error/noindex.html", [web_sg.title])

    return template
