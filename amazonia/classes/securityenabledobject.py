from troposphere import Template, ec2, Ref, Tags


class SecurityEnabledObject(Template):
    def __init__(self, vpc, title):
        """

            A Class to enable uni-directional flow when given two security groups

        """
        super(object, self).__init__()
        self.title = title
        self.securitygroup = self.create_security_group(vpc)


    def addFlow(self, other, port, protocol):
        self.add_egress(other, port, protocol)
        other.add_ingress(self, port, protocol)


    def add_ingress(self, other, port, protocol):
        name = self.title + port + "From" + other.title + port
        self.add_resource(ec2.SecurityGroupIngress(name,
                                                   IpProtocol=protocol,
                                                   FromPort=port,
                                                   ToPort=port,
                                                   GroupId=Ref(self.securitygroup)
                                                   ))


    def add_egress(self, other, port, protocol):
        name = self.title + port + "To" + other.title + port
        self.add_resource(ec2.SecurityGroupEgress(name,
                                                  IpProtocol=protocol,
                                                  FromPort=port,
                                                  ToPort=port,
                                                  GroupId=Ref(self.securitygroup)
                                                  ))

    def create_security_group(self, vpc, title):
        name = self.title + "SecurityGroup"
        self.add_resource(ec2.SecurityGroup(name,
                                            GroupDescription="Security group",
                                            VpcId=Ref(vpc),
                                            Tags=Tags(Name=name)
                                            ))

