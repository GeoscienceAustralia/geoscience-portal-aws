#!/usr/bin/python3

from amazonia.classes.securityenabledobject import SecurityEnabledObject
from troposphere import Tags, Ref
import troposphere.elasticloadbalancing as elb


class Elb(SecurityEnabledObject):

    def __init__(self, **kwargs):
        """
        Public Class to create a ELB in the unit stack environment
        ELB - AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html
        ELB - Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/elasticloadbalancing.py
        :param protocol: Single protocol to allow traffic e.g.  HTTP, HTTPS, TCP or SSL
        :param port: Single port to allow traffic in and out of the load balancer.
         e.g. Listener Port and Health Check Target port - 80, 8080, 443
        :param path2ping: Path for the Healthcheck to ping e.g 'index.html' or 'test/test_page.htm'
        :param subnets: List of subnets either [pub_sub_list] if public unit or [pri_sub_list] if private unit
        :param title: Name of the Cloud formation elb object


        """
        super(Elb, self).__init__(vpc=kwargs['vpc'], title=kwargs['title'], stack=kwargs['stack'])

        self.elb = self.stack.add_resource(
                    elb.LoadBalancer(kwargs['title'],
                                     CrossZone=True,
                                     HealthCheck=elb.HealthCheck(Target='{0}:{1}/{2}'.format(kwargs['protocol'].upper(),
                                                                                             kwargs['port'],
                                                                                             kwargs['path2ping']),
                                                                 HealthyThreshold='2',
                                                                 UnhealthyThreshold='5',
                                                                 Interval='10',
                                                                 Timeout='5'),
                                     Listeners=[elb.Listener(LoadBalancerPort=kwargs['port'],
                                                             Protocol=kwargs['protocol'].upper(),
                                                             InstancePort=kwargs['port'],
                                                             InstanceProtocol=kwargs['protocol'].upper())],
                                     Scheme='internet-facing',
                                     SecurityGroups=[Ref(self.security_group)],
                                     Subnets=[Ref(x) for x in kwargs['subnets']],
                                     Tags=Tags(Name=kwargs['title'])))
        # TODO Add Output for ELB Address
        # TODO If kwarg['subnets']==pri_sub_list e.g Private unit, Scheme must be set to 'internal'
        # TODO Elb Unit Tests:
        # TODO Unit Tests:jump_sg = jumphost1.NetworkInterfaces.GroupSet,
        # TODO Sys Tests: Connect from jumphost to subpub1 instance, subpub2 instance, can't connect on port 80,8080,443
        # TODO Sys Tests: Try connecting to host in another vpc

