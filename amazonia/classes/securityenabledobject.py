from troposphere import Template, ec2, Ref, Tags, GetAtt, Join


class SecurityEnabledObject(Template):
    def __init__(self, vpc, title):
        """
        A Class to enable uni-directional flow when given two security groups
        :param vpc: The VPC for this object
        :param title: the Title of the object eg: unit01ELB, unit01ASG
        :return: a security group, and the ability to create ingress and egress rules
        """
        super(SecurityEnabledObject, self).__init__()
        self.title = title
        self.security_group = self.create_security_group(vpc)

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
        :param other: The SecurityEnabledObject that we are expecting traffic from
        :param port: Port to send, and receive traffic on
        :param protocol: Protocol to send, and receive traffic on
        """
        name = self.title + port + "From" + other.title + port
        self.add_resource(ec2.SecurityGroupIngress(name,
                                                   IpProtocol=protocol,
                                                   FromPort=port,
                                                   ToPort=port,
                                                   GroupId=Ref(self.security_group),
                                                   SourceSecurityGroupId=GetAtt(other.security_group.title, "GroupId")
                                                   ))

    def add_egress(self, other, port, protocol):
        """
        Add an egress rule to this SecurityEnabledObject
        :param other: The SecurityEnabledObject that will be sending traffic to this SecurityEnabledObject
        :param port: Port to send, and receive traffic on
        :param protocol: Protocol to send, and receive traffic on
        :return:
        """
        name = self.title + port + "To" + other.title + port
        self.add_resource(ec2.SecurityGroupEgress(name,
                                                  IpProtocol=protocol,
                                                  FromPort=port,
                                                  ToPort=port,
                                                  GroupId=Ref(self.security_group),
                                                  DestinationSecurityGroupId=GetAtt(other.security_group.title, "GroupId")
                                                  ))

    def create_security_group(self, vpc):
        """
        Add a security group to this SecurityEnabledObject which can then have rules added to it where needed
        :param vpc: The VPC that the security group should live in
        :return: The security group for this SecurityEnabledObject
        """
        name = self.title + "SG"
        return self.add_resource(
                    ec2.SecurityGroup(
                        name,
                        GroupDescription="Security group",
                        VpcId=Ref(vpc),
                        Tags=Tags(Name=Join("", [Ref('AWS::StackName'), '-', name]))
                        ))
