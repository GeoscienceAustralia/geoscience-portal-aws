#!/usr/bin/python3

from amazonia.classes.securityenabledobject import SecurityEnabledObject
from troposphere import Tags, Ref, Output, Join, GetAtt, route53
import troposphere.elasticloadbalancing as elb


class Elb(SecurityEnabledObject):

    def __init__(self, **kwargs):
        """
        Public Class to create a ELB in the unit stack environment
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/elasticloadbalancing.py
        :param protocol: Single protocol to allow traffic e.g.  HTTP, HTTPS, TCP or SSL
        :param port: Single port to allow traffic in and out of the load balancer.
         e.g. Listener Port and Health Check Target port - 80, 8080, 443
        :param path2ping: Path for the Healthcheck to ping e.g 'index.html' or 'test/test_page.htm'
        :param subnets: List of subnets either [pub_sub_list] if public unit or [pri_sub_list] if private unit
        :param title: Name of the Cloud formation elb object
        :param hosted_zone_id: Route53 hosted zone ID
        """
        self.title = kwargs['title'] + 'Elb'
        super(Elb, self).__init__(vpc=kwargs['vpc'], title=self.title, template=kwargs['template'])

        self.elb = self.template.add_resource(
                    elb.LoadBalancer(self.title,
                                     CrossZone=True,
                                     HealthCheck=elb.HealthCheck(Target=kwargs['protocol'].upper() + ':' +
                                                                 kwargs['port'] + kwargs['path2ping'],
                                                                 HealthyThreshold='10',
                                                                 UnhealthyThreshold='2',
                                                                 Interval='300',
                                                                 Timeout='60'),
                                     Listeners=[elb.Listener(LoadBalancerPort=kwargs['port'],
                                                             Protocol=kwargs['protocol'].upper(),
                                                             InstancePort=kwargs['port'],
                                                             InstanceProtocol=kwargs['protocol'].upper())],
                                     Scheme='internet-facing',
                                     SecurityGroups=[Ref(self.security_group)],
                                     Subnets=[Ref(x) for x in kwargs['subnets']],
                                     Tags=Tags(Name=self.title)))

        self.elb_r53 = self.template.add_resource(route53.RecordSetType(
                                                             self.title + 'R53',
                                                             HostedZoneId=kwargs['hosted_zone_id'],
                                                             Name=Join('', [self.title, 'R53', '.']),
                                                             ResourceRecords=[GetAtt(self.elb, 'DNSName')],
                                                             TTL=300,
                                                             Type='CNAME'))

        self.template.add_output(Output(
            self.elb.title,
            Description='URL of the {0} website'.format(self.elb.title),
            Value=Join('', ['http://', self.elb_r53.Name])
        ))

        # TODO If kwarg['subnets']==pri_sub_list e.g Private unit, Scheme must be set to 'internal'
        # TODO Sys Tests: Connect from jumphost to subpub1 instance, subpub2 instance, can't connect on port 80,8080,443
        # TODO Sys Tests: Try connecting to host in another vpc

