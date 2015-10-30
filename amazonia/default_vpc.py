# pylint: disable=missing-docstring, invalid-name, line-too-long, redefined-outer-name, too-many-arguments

"""Geoscience Portal AWS VPC
"""

from . import name_tag, http_ingress, icmp_ingress, ssh_ingress_from_ga
from troposphere import Ref, Tags
import troposphere.ec2 as ec2

DEFAULT_NAT_IMAGE_ID = "ami-893f53b3"
DEFAULT_NAT_INSTANCE_TYPE = "t2.micro"

def _add_nat(template, vpc, public_subnet, image_id, instance_type, key_pair_name, nat_ip):
    nat_sg_id = "NatSecurityGroup"
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
    nat_id = "NAT"
    nat = template.add_resource(ec2.Instance(
        nat_id,
        SecurityGroupIds=[Ref(nat_sg.title)],
        KeyName=key_pair_name,
        SubnetId=Ref(public_subnet.title),
        ImageId=image_id,
        InstanceType=instance_type,
        Tags=Tags(
            Name=name_tag(nat_id),
        ),
    ))
    template.add_resource(ec2.EIPAssociation(
        nat.title + "IpAssociation",
        EIP=nat_ip,
        InstanceId=Ref(nat.title)
    ))
    return nat


def _add_public_subnet(template, vpc):
    title = "PublicSubnet"
    public_subnet = template.add_resource(ec2.Subnet(
        title,
        VpcId=Ref(vpc.title),
        CidrBlock="10.0.0.0/24",
        Tags=Tags(
            Name=name_tag(title)
        ),
    ))
    internet_gateway = _add_internet_gateway(template, vpc)

    route_table_id = "PublicRouteTable"
    route_table = template.add_resource(ec2.RouteTable(
        route_table_id,
        VpcId=Ref(vpc.title),
        Tags=Tags(
            Name=name_tag(route_table_id),
        ),
    ))
    template.add_resource(ec2.SubnetRouteTableAssociation(
        "PublicRouteTableAssociation",
        SubnetId=Ref(public_subnet.title),
        RouteTableId=Ref(route_table),
    ))
    template.add_resource(ec2.Route(
        "InboundRoute",
        GatewayId=Ref(internet_gateway.title),
        RouteTableId=Ref(route_table.title),
        DestinationCidrBlock="0.0.0.0/0",
    ))
    return public_subnet

def _add_private_subnet(template, vpc, nat):
    title = "PrivateSubnet"
    private_subnet = template.add_resource(ec2.Subnet(
        title,
        VpcId=Ref(vpc.title),
        CidrBlock="10.0.1.0/24",
        Tags=Tags(
            Name=name_tag(title)
        ),
    ))
    route_table_id = "PrivateRouteTable"
    route_table = template.add_resource(ec2.RouteTable(
        route_table_id,
        VpcId=Ref(vpc.title),
        Tags=Tags(
            Name=name_tag(title),
        ),
    ))
    template.add_resource(ec2.SubnetRouteTableAssociation(
        "PrivateRouteTableAssociation",
        SubnetId=Ref(private_subnet.title),
        RouteTableId=Ref(route_table),
    ))
    template.add_resource(ec2.Route(
        "OutboundRoute",
        InstanceId=Ref(nat.title),
        RouteTableId=Ref(route_table.title),
        DestinationCidrBlock="0.0.0.0/0",
    ))
    return private_subnet

def add_vpc(template, key_pair_name, nat_ip, nat_image_id=DEFAULT_NAT_IMAGE_ID, nat_instance_type=DEFAULT_NAT_INSTANCE_TYPE):
    vpcId = "VPC"
    vpc = template.add_resource(ec2.VPC(
        vpcId,
        CidrBlock="10.0.0.0/16",
        Tags=Tags(
            Name=name_tag(vpcId)
        ),
    ))
    public_subnet = _add_public_subnet(template, vpc)
    nat = _add_nat(template, vpc, public_subnet, nat_image_id, nat_instance_type, key_pair_name, nat_ip)
    _add_private_subnet(template, vpc, nat)
    return vpc

def _add_internet_gateway(template, vpc):
    gatewayId = "InternetGateway"
    internet_gateway = template.add_resource(ec2.InternetGateway(
        gatewayId,
        Tags=Tags(
            Name=name_tag(gatewayId),
        ),
    ))
    attachmentId = "InternetGatewayAttachment"
    template.add_resource(ec2.VPCGatewayAttachment(
        attachmentId,
        VpcId=Ref(vpc.title),
        InternetGatewayId=Ref(internet_gateway.title),
    ))
    return internet_gateway

def private_subnet(template):
    return template.resources["PrivateSubnet"]
