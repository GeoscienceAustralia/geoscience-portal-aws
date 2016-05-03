#!/usr/bin/python3

from amazonia.classes.security_enabled_object import SecurityEnabledObject
from troposphere import Tags, Ref, Output, Join, GetAtt, route53
import troposphere.elasticloadbalancing as elb


class Elb(SecurityEnabledObject):

    def __init__(self, title, vpc, template, protocol, loadbalancerport, instanceport, path2ping, subnets, gateway_attachment, **kwargs):
        """
        Public Class to create an Elastic Loadbalancer in the unit stack environment
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/elasticloadbalancing.py
        :param title: Name of the Cloud formation stack object
        :param vpc: The vpc object to add the Elastic Loadbalancer to.
        :param template: The troposphere template to add the Elastic Loadbalancer to.
        :param protocol: Single protocol to allow traffic. This must be in CAPITALS e.g.  HTTP, HTTPS, TCP or SSL
        :param loadbalancerport: Single string representing a port to Listen for traffic on the load balancer.
        :param instanceport: Single string representing a port for the load balancer to use when talking to instances.
        :param path2ping: Path for the Healthcheck to ping e.g 'index.html' or 'test/test_page.htm'
        :param subnets: List of subnets either [pub_sub_list] if public unit or [pri_sub_list] if private unit
        :param hosted_zone_name: Route53 hosted zone ID
        :param gateway_attachment: Stack's gateway attachment troposphere object
        """
        self.title = title + 'Elb'
        super(Elb, self).__init__(vpc=vpc, title=self.title, template=template)

        self.trop_elb = self.template.add_resource(
                    elb.LoadBalancer(self.title,
                                     CrossZone=True,
                                     HealthCheck=elb.HealthCheck(Target=protocol + ':' + instanceport + path2ping,
                                                                 HealthyThreshold='10',
                                                                 UnhealthyThreshold='2',
                                                                 Interval='300',
                                                                 Timeout='60'),
                                     Listeners=[elb.Listener(LoadBalancerPort=loadbalancerport,
                                                             Protocol=protocol,
                                                             InstancePort=instanceport,
                                                             InstanceProtocol=protocol)],
                                     Scheme='internet-facing',
                                     SecurityGroups=[Ref(self.security_group)],
                                     Subnets=[Ref(x) for x in subnets],
                                     Tags=Tags(Name=self.title)))
        self.trop_elb.DependsOn = gateway_attachment.title

        if kwargs['hosted_zone_name']:
            self.elb_r53 = self.template.add_resource(route53.RecordSetType(
                                                             self.title + 'R53',
                                                             HostedZoneName=kwargs['hosted_zone_name'],
                                                             Name=Join('', [self.title,
                                                                            'R53',
                                                                            '.',
                                                                            kwargs['hosted_zone_name']]),
                                                             ResourceRecords=[GetAtt(self.trop_elb, 'DNSName')],
                                                             TTL=300,
                                                             Type='CNAME'))

            self.template.add_output(Output(
                self.trop_elb.title,
                Description='URL of the {0} ELB'.format(self.title),
                Value=Join('', ['http://', self.elb_r53.Name])
            ))

        else:
            self.template.add_output(Output(
                self.trop_elb.title,
                Description='URL of the {0} ELB'.format(self.title),
                Value=Join('', ['http://', GetAtt(self.trop_elb, 'DNSName')])
            ))
