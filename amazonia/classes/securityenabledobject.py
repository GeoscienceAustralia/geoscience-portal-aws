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

        self.stack = kwargs['stack']
        self.title = kwargs['title']
        self.security_group = self.create_security_group(kwargs['vpc'])
        self.ingress = []
        self.egress = []

    def add_flow(self, other, port, protocol):
        """
        A function that will add security group rules to 'other' from this SecurityEnabledObject.
        Including an incoming rule on the 'other' SecurityEnabledObject
        :param other: Traffic 'receiving' SecurityEnabledObject
        :param port: Port to send, and receive traffic on
        :param protocol: Protocol to send, and receive traffic on
        """
        other.add_ingress(self, port, protocol)
        self.add_egress(other, port, protocol)

    def add_ingress(self, other, port, protocol):
        """
        Add an ingress rule to this SecurityEnabledObject
        Creates a Troposphere SecurityGroupIngress object
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param other: The SecurityEnabledObject that we are expecting traffic from
        :param port: Port to send, and receive traffic on
        :param protocol: Protocol to send, and receive traffic on
        """
        name = self.title + port + "From" + other.title + port
        self.ingress.append(self.stack.add_resource(ec2.SecurityGroupIngress(
            name,
            IpProtocol=protocol,
            FromPort=port,
            ToPort=port,
            GroupId=Ref(self.security_group),
            SourceSecurityGroupId=GetAtt(other.security_group.title, "GroupId")
            )))

    def add_egress(self, other, port, protocol):
        """
        Add an egress rule to this SecurityEnabledObject
        Creates a Troposphere SecurityGroupEgress object
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param other: The SecurityEnabledObject that will be sending traffic to this SecurityEnabledObject
        :param port: Port to send, and receive traffic on
        :param protocol: Protocol to send, and receive traffic on
        """
        name = self.title + port + "To" + other.title + port
        self.egress.append(self.stack.add_resource(ec2.SecurityGroupEgress(
            name,
            IpProtocol=protocol,
            FromPort=port,
            ToPort=port,
            GroupId=Ref(self.security_group),
            DestinationSecurityGroupId=GetAtt(other.security_group.title, "GroupId")
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
        name = self.title + "Sg"
        return self.stack.add_resource(
                    ec2.SecurityGroup(
                        name,
                        GroupDescription="Security group",
                        VpcId=Ref(vpc),
                        Tags=Tags(Name=Join("", [Ref('AWS::StackName'), '-', name]))
                        ))
