#!/usr/bin/python3

from troposphere import ec2, Ref, Tags, GetAtt, Join


class SecurityEnabledObject(object):
    def __init__(self, **kwargs):
        """
        A Class to enable uni-directional flow when given two security groups
        :param stack: The VPC for this object
        :param vpc: The VPC for this object
        :param title: the Title of the object eg: unit01ELB, unit01ASG
        :return: a security group, and the ability to create ingress and egress rules
        """

        super(SecurityEnabledObject, self).__init__()

        self.template = kwargs['template']
        self.title = kwargs['title']
        self.security_group = self.create_security_group(kwargs['vpc'])
        self.ingress = []
        self.egress = []

    def add_flow(self, other, port):
        """
        A function that will add security group rules to 'other' from this SecurityEnabledObject.
        Including an incoming rule on the 'other' SecurityEnabledObject
        :param other: Traffic 'receiving' SecurityEnabledObject
        :param port: Port to send, and receive traffic on
        :param protocol: Protocol to send, and receive traffic on
        """
        other.add_ingress(self, port)
        self.add_egress(other, port)

    def add_ingress(self, other, port):
        """
        Add an ingress rule to this SecurityEnabledObject
        Creates a Troposphere SecurityGroupIngress object
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param other: The SecurityEnabledObject that we are expecting traffic from
        :param port: Port to send, and receive traffic on
        :param protocol: Protocol to send, and receive traffic on
        """

        name = self.title + port + 'From' + other.title + port
        self.ingress.append(self.template.add_resource(ec2.SecurityGroupIngress(
            name,
            IpProtocol='tcp',
            FromPort=port,
            ToPort=port,
            GroupId=Ref(self.security_group),
            SourceSecurityGroupId=GetAtt(other.security_group.title, 'GroupId')
            )))

    def add_egress(self, other, port):
        """
        Add an egress rule to this SecurityEnabledObject
        Creates a Troposphere SecurityGroupEgress object
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param other: The SecurityEnabledObject that will be sending traffic to this SecurityEnabledObject
        :param port: Port to send, and receive traffic on
        :param protocol: Protocol to send, and receive traffic on
        """
        name = self.title + port + 'To' + other.title + port
        self.egress.append(self.template.add_resource(ec2.SecurityGroupEgress(
            name,
            IpProtocol='tcp',
            FromPort=port,
            ToPort=port,
            GroupId=Ref(self.security_group),
            DestinationSecurityGroupId=GetAtt(other.security_group.title, 'GroupId')
            )))

    def add_si_ingress(self, other, port):
        """
        Add an ingress rule for Jumpboxes to this SecurityEnabledObject
        Creates a Troposphere SecurityGroupIngress object
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param other:  CIDRs for limiting traffic to nats to only company, e.g. 124.47.122.122/32 or 0.0.0.0/0 for public'
        :param port: Port to allow traffic
        """
        name = self.title + port + 'From' + self.ip(other) + port
        self.ingress.append(self.template.add_resource(ec2.SecurityGroupIngress(
            name,
            IpProtocol='tcp',
            FromPort=port,
            ToPort=port,
            GroupId=Ref(self.security_group),
            CidrIp=other
        )))

    def add_si_egress(self, other, port):
        """
        Add an egress rule for this security enabled object for traffic from NATs to public internet
        Creates a Troposphere SecurityGroupEgress object
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param other:  CIDRs for limiting traffic from nats, e.g. 124.47.122.122/32 or 0.0.0.0/0 for public'
        :param port: Port to allow traffic
        """
        name = self.title + port + 'To' + self.ip(other) + port
        self.egress.append(self.template.add_resource(ec2.SecurityGroupEgress(
            name,
            IpProtocol='tcp',
            FromPort=port,
            ToPort=port,
            GroupId=Ref(self.security_group),
            CidrIp=other
        )))

    def create_security_group(self, vpc):
        """
        Add a security group to this SecurityEnabledObject which can then have rules added to it where needed
        Creates a Troposphere SecurityGroup object
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param vpc: The VPC that the security group should live in
        :return: The security group for this SecurityEnabledObject
        """
        name = self.title + 'Sg'
        return self.template.add_resource(
                    ec2.SecurityGroup(
                        name,
                        GroupDescription='Security group',
                        VpcId=Ref(vpc),
                        Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', name]))
                        ))

    @staticmethod
    def ip(cidr):
        """
        Function to return cloudformation friendly format of ip address to use in cf object titles.
        :param cidr: CIDRs for limiting traffic to nats to only company, e.g. 124.47.122.122/32 or 0.0.0.0/0 for public'
        :return: ip address without punctuation for use in titles e.g. 124o47o122o122
        """
        ip = cidr.split('/')         # Split CIDR up at '/'
        ip_x = 'x'.join(ip)                 # Remove subnmask element replace with x e.g. '124.47.122.122x32'
        ip_split = ip_x.split('.')          # Split remaining string by octects
        ip_xo = 'o'.join(ip_split)          # Join IP with 'o' instead of octects or submask using e.g. '124o47o122o122x32'

        return ip_xo
