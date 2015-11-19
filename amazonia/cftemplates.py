# pylint: disable=too-many-arguments

""" Templates to implement common cloud formation configurations

The functions in this module generate cloud formation scripts that install common AWS environments and components

"""

from . import name_tag, http_ingress, https_ingress, icmp_ingress, ssh_ingress_from_ga
from troposphere import Ref, Tags
import troposphere.ec2 as ec2

DEFAULT_NAT_IMAGE_ID = "ami-893f53b3"
DEFAULT_NAT_INSTANCE_TYPE = "t2.micro"
SYSTEM_NAME="TestApplication"
ENVIRONMENT_NAME="Experimental"

#CIDRs
VPC_CIDR = "10.0.0.0/16" 
PUBLIC_SUBNET_AZ1_CIDR = "10.0.0.0/24"
PRIVATE_SUBNET_AZ1_CIDR = "10.0.10/24"
PUBLIC_SUBNET_NAME = "PublicSubnet"
PRIVATE_SUBNET_NAME = "PrivateSubnet"


# number of subnets created
num_subnets = 0
num_route_tables = 0
num_internet_gateways = 0
num_routes = 0
num_nats = 0




def create_vpc(template, VPCName, CidrBlock, key_pair_name):
    """Create a VPC resource and add it to the given template."""
    vpc = template.add_resource(ec2.VPC(VPCName,
                                        CidrBlock=VPC_CIDR,
                                        Tags=Tags(Name=name_tag(VPCName),
                                                  Environment=ENVIRONMENT_NAME)))  
    return vpc


def addSingleAZenv(template, vpc):
	""" Public function to create a single AZ environment in a vpc """
        # configure network
	public_subnet = add_subnet(template, vpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
	public_route_table = add_route_table(template, vpc, public_subnet)
	internet_gateway = add_internet_gateway(template, vpc, public_route_table)
        private_subnet = add_subnet(template, vpc, PRIVATE_SUBNET_NAME, PRIVATE_SUBNET_AZ1_CIDR)
        private_route_table = add_route_table(template, vpc, private_subnet)
        # add_route_outbound_via_NAT(template, private_route_table, nat):
        
    

	return template

def add_subnet(template, vpc, name, cidr):
    global num_subnets
    num_subnets=num_subnets+1
    title = name + str(num_subnets)
    public_subnet = template.add_resource	(ec2.Subnet(title,
                                                            VpcId=Ref(vpc.title),
                                                            CidrBlock=cidr,
                                                            Tags=Tags(Name=name_tag(title),
                                                                      Environment=ENVIRONMENT_NAME)
    ))
    return public_subnet


								
def add_route_table(template, vpc, subnet):

	global num_route_tables
	num_route_tables = num_route_tables + 1

	# create the route table in the VPC
	route_table_id = "PublicRouteTable" + str(num_route_tables)
	route_table = template.add_resource(ec2.RouteTable(route_table_id,
                                                           VpcId=Ref(vpc.title),
                                                           Tags=Tags(Name=name_tag(route_table_id)),))
	
	# Associate the route table with the subnet
	template.add_resource(ec2.SubnetRouteTableAssociation(
		route_table_id + "Association",
		SubnetId=Ref(subnet.title),
		RouteTableId=Ref(route_table),
	))
	return route_table
	

def add_internet_gateway(template, vpc, route_table):
	global num_internet_gateways
	num_internet_gateways = num_internet_gateways + 1
	internet_gateway_title = "InternetGateway" + str(num_internet_gateways)

        internet_gateway = template.add_resource(ec2.InternetGateway(internet_gateway_title,
                                                                     Tags=Tags(Name=name_tag(internet_gateway_title),
                                                                               Environment=ENVIRONMENT_NAME)

        ))

        attachment_title = internet_gateway_title + "Attachment"
        template.add_resource(ec2.VPCGatewayAttachment(attachment_title,
                                                       VpcId=Ref(vpc.title),
                                                       InternetGatewayId=Ref(internet_gateway.title),
        ))

	global num_routes 
	num_routes = num_routes + 1
	template.add_resource(ec2.Route(
		"InboundRoute" + str(num_routes),
		GatewayId=Ref(internet_gateway.title),
		RouteTableId=Ref(route_table.title),
		DestinationCidrBlock="0.0.0.0/0",
	))
        return internet_gateway


def add_route_public_ingress(template, route_table, internet_gateway):
	global num_routes 
	num_routes = num_routes + 1
	template.add_resource(ec2.Route(
		"InboundRoute" + str(num_routes),
		GatewayId=Ref(internet_gateway.title),
		RouteTableId=Ref(route_table.title),
		DestinationCidrBlock="0.0.0.0/0",
	))



def add_nat(template, vpc, public_subnet, image_id, instance_type, key_pair_name):
    nat_sg_id = "NatSecurityGroup" + num
    nat_sg = template.add_resource(ec2.SecurityGroup(
        nat_sg_id,
        GroupDescription="Security group for NAT instance",
        VpcId=Ref(vpc.title),
        Tags=Tags(
            Name=name_tag(nat_sg_id)
        ),
    ))
    template.add_resource(ssh_ingress_from_ga(nat_sg))
    template.add_resource(icmp_ingress(nat_sg))
    template.add_resource(http_ingress(nat_sg))
    template.add_resource(https_ingress(nat_sg))
    nat_id = "NAT" + num
    nat = template.add_resource(ec2.Instance(
        nat_id,
        SecurityGroupIds=[Ref(nat_sg.title)],
        KeyName=key_pair_name,
        SubnetId=Ref(public_subnet.title),
        ImageId=image_id,
        InstanceType=instance_type,
        SourceDestCheck=False,
        PrivateIpAddress="10.0.0.100",
        Tags=Tags(
            Name=name_tag(nat_id),
        ),
    ))
    template.add_resource(ec2.EIPAssociation(
        nat.title + "IpAssociation" + num,
        EIP=nat_ip,
        InstanceId=Ref(nat.title)
    ))
    return nat

        
def add_route_outbound_via_NAT(template, route_table, nat):
	global num_routes 
	num_routes = num_routes + 1

        template.add_resource(ec2.Route("OutboundRoute" + str(num_routes),
                                        InstanceId=Ref(nat.title),
                                        RouteTableId=Ref(route_table.title),
                                        DestinationCidrBlock="0.0.0.0/0",
        ))


def private_subnet(template, name):
    """Extract and return the specified subnet resource from the given template."""
    return template.resources[name]

def nat_instance(template):
    """Extract and return the NAT instance from the given template."""
    return template.resources["NAT"]

def _add_nat(template, vpc, public_subnet, image_id, instance_type, key_pair_name, nat_ip, num=""):
    nat_sg_id = "NatSecurityGroup" + num
    nat_sg = template.add_resource(ec2.SecurityGroup(
        nat_sg_id,
        GroupDescription="Security group for NAT instance",
        VpcId=Ref(vpc.title),
        Tags=Tags(
            Name=name_tag(nat_sg_id)
        ),
    ))
    template.add_resource(ssh_ingress_from_ga(nat_sg))
    template.add_resource(icmp_ingress(nat_sg))
    template.add_resource(http_ingress(nat_sg))
    template.add_resource(https_ingress(nat_sg))
    nat_id = "NAT" + num
    nat = template.add_resource(ec2.Instance(
        nat_id,
        SecurityGroupIds=[Ref(nat_sg.title)],
        KeyName=key_pair_name,
        SubnetId=Ref(public_subnet.title),
        ImageId=image_id,
        InstanceType=instance_type,
        SourceDestCheck=False,
        PrivateIpAddress="10.0.0.100",
        Tags=Tags(
            Name=name_tag(nat_id),
        ),
    ))
    template.add_resource(ec2.EIPAssociation(
        nat.title + "IpAssociation" + num,
        EIP=nat_ip,
        InstanceId=Ref(nat.title)
    ))
    return nat


def _add_private_subnet(template, vpc, nat, num=""):
    title = "PrivateSubnet" + num
    subnet = template.add_resource(ec2.Subnet(
        title,
        VpcId=Ref(vpc.title),
        CidrBlock="10.0.1.0/24",
        Tags=Tags(
            Name=name_tag(title)
        ),
    ))
    route_table_id = "PrivateRouteTable" + num
    route_table = template.add_resource(ec2.RouteTable(
        route_table_id,
        VpcId=Ref(vpc.title),
        Tags=Tags(
            Name=name_tag(title),
        ),
    ))
    template.add_resource(ec2.SubnetRouteTableAssociation(
        "PrivateRouteTableAssociation" + num,
        SubnetId=Ref(subnet.title),
        RouteTableId=Ref(route_table),
    ))
    template.add_resource(ec2.Route(
        "OutboundRoute" + num,
        InstanceId=Ref(nat.title),
        RouteTableId=Ref(route_table.title),
        DestinationCidrBlock="0.0.0.0/0",
    ))
    return private_subnet



