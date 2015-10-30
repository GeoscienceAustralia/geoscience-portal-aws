# pylint: disable=missing-docstring, invalid-name, line-too-long, redefined-outer-name, too-many-arguments

from troposphere import Join, Ref
import troposphere.ec2 as ec2

PUBLIC_GA_GOV_AU_PTR = '192.104.44.129'

def name_tag(suffix):
    return Join('', [
        Ref('AWS::StackName'),
        '-',
        suffix])

def ssh_ingress_from_ga(security_group):
    return ssh_ingress(security_group, PUBLIC_GA_GOV_AU_PTR + '/32')

def ssh_ingress(security_group, cidr='0.0.0.0/0'):
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
    title = security_group.title + 'IngressHTTP'
    return ec2.SecurityGroupIngress(
        title,
        IpProtocol='tcp',
        FromPort='80',
        ToPort='80',
        GroupId=Ref(security_group.title),
        CidrIp=cidr
    )

def icmp_ingress(security_group, cidr='0.0.0.0/0'):
    title = security_group.title + 'IngressICMP'
    return ec2.SecurityGroupIngress(
        title,
        IpProtocol='icmp',
        FromPort='-1',
        ToPort='-1',
        GroupId=Ref(security_group.title),
        CidrIp=cidr
    )
