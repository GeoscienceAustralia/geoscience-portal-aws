"""Useful utility functions"""

from troposphere import Join, Ref
import troposphere.ec2 as ec2

PUBLIC_GA_GOV_AU_PTR = '192.104.44.129'

def stack_name_tag():
    return "Ref('AWS::StackName')" 

def name_tag(resource_name):
    """Prepend stack name to the given resource name."""
    return Join("", [Ref('AWS::StackName'), '-', resource_name])

def ssh_ingress_from_ga(security_group):
    """Return an ingress for the given security group to allow
    SSH traffic from public.ga.gov.au."""

    return ssh_ingress(security_group, PUBLIC_GA_GOV_AU_PTR + '/32')

def ssh_ingress(security_group, cidr='0.0.0.0/0'):
    """Return an ingress for the given security group to allow SSH traffic."""
    title = security_group.title + 'IngressSSH'
    return ec2.SecurityGroupIngress(
        title,
        IpProtocol='tcp',
        FromPort='22',
        ToPort='22',
        GroupId=Ref(security_group.title),
        CidrIp=cidr
    )

def http_ingress(security_group, cidr='0.0.0.0/0'):
    """Return an ingress for the given security group to allow HTTP traffic."""
    title = security_group.title + 'IngressHTTP'
    return ec2.SecurityGroupIngress(
        title,
        IpProtocol='tcp',
        FromPort='80',
        ToPort='80',
        GroupId=Ref(security_group.title),
        CidrIp=cidr
    )

def https_ingress(security_group, cidr='0.0.0.0/0'):
    """Return an ingress for the given security group to allow HTTPS traffic."""
    title = security_group.title + 'IngressHTTPS'
    return ec2.SecurityGroupIngress(
        title,
        IpProtocol='tcp',
        FromPort='443',
        ToPort='443',
        GroupId=Ref(security_group.title),
        CidrIp=cidr
    )

def icmp_ingress(security_group, cidr='0.0.0.0/0'):
    """Return an ingress for the given security group to allow ICMP traffic."""
    title = security_group.title + 'IngressICMP'
    return ec2.SecurityGroupIngress(
        title,
        IpProtocol='icmp',
        FromPort='-1',
        ToPort='-1',
        GroupId=Ref(security_group.title),
        CidrIp=cidr
    )
