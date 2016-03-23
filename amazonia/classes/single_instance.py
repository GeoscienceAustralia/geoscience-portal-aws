#!/usr/bin/env python

from troposphere import Ref, Tags, Join, Output, GetAtt, ec2
from amazonia.classes.securityenabledobject import SecurityEnabledObject


class SingleInstance(SecurityEnabledObject):
    def __init__(self, **kwargs):
        """
        Create a singleton instance such as a nat or a jumphost
        :param kwargs: Key value pairs required to create a single instance
            title: Title of instance e.g 'nat1', 'nat2' or 'jump1'
            keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
            si_image_id: AWS ami id to create instance from, e.g. 'ami-12345'
            si_instance_type: Instance type for single instance e.g. 't2.micro' or 't2.nano'
            vpc: Troposphere vpc object, required for SecurityEnabledObject class
            subnet: Troposhere object for subnet created e.g. 'sub_pub1'
        """

        super(SingleInstance, self).__init__(kwargs['vpc'], kwargs['title'])

        self.single = self.add_resource(
                           ec2.Instance(
                               kwargs['title'],
                               KeyName=kwargs['keypair'],
                               ImageId=kwargs['si_image_id'],
                               InstanceType=kwargs['si_instance_type'],
                               NetworkInterfaces=[ec2.NetworkInterfaceProperty(
                                   GroupSet=[Ref(self.security_group)],
                                   AssociatePublicIpAddress=True,
                                   DeviceIndex="0",
                                   DeleteOnTermination=True,
                                   SubnetId=Ref(kwargs['subnet']),
                               )],
                               SourceDestCheck=False if kwargs['title'][:3].lower() == 'nat' else True,
                               Tags=Tags(Name=Join("", [Ref('AWS::StackName'), '-', kwargs['title']]))
                           ))

        if self.single.SourceDestCheck == 'true':
            self.si_output(nat=False, subnet=kwargs['subnet'])
        else:
            self.si_output(nat=True, subnet=kwargs['subnet'])

    def si_output(self, **kwargs):
        """
        Function that add the IP output required for single instances depending if it is a NAT or JumpHost
        :param kwargs: Key value pairs required to create output for a single instance
            nat: A NAT boolean is defined by the SourceDestCheck=False flag for extracting the ip
            subnet: A subnetwhere the instance lives required for output.
        :return: Troposphere Output object containing IP details
        """

        if kwargs['nat'] is True:
            net_interface = "PrivateIp"
        else:
            net_interface = "PublicIp"

        self.add_output(
             Output(
                 self.single.title,
                 Description='{0} address of {1} single instance'.format(net_interface, self.single.title),
                 Value=Join(" ", ["{0} {1} address".format(self.single.title, net_interface),
                                  GetAtt(self.single, net_interface),
                                  "on subnet",
                                  Ref(kwargs['subnet'])
                                  ]
                            )
                 ))

    # TODO NAT Security Group Unit Tests: validate that nat_sg = nat.NetworkInterfaces.GroupSet
    # TODO Unit Tests:jump_sg = jumphost1.NetworkInterfaces.GroupSet,
    # TODO Sys Tests: Connect from jumphost to subpub1 instance, subpub2 instance, can't connect on port 80,8080,443
    # TODO Sys Tests: Try connecting to host in another vpc
