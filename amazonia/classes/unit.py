#!/usr/bin/python3
#  pylint: disable=too-many-arguments, line-too-long

from amazonia.classes.asg import Asg
from amazonia.classes.elb import Elb


class Unit(object):
    def __init__(self, **kwargs):
        """
        Create an Amazonia unit, with associated Amazonia ELB and ASG
        :param title: Title of the autoscaling application  prefixedx with Stack name e.g 'MyStackWebApp1',
         'MyStackApi2' or 'MyStackDataprocessing'
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param stack: Troposphere stack to append resources to
        :param protocol: protocol for ELB and webserver to communicate via
        :param port: port for ELB and webserver to communicate via
        :param path2ping: path for ELB healthcheck
        :param public_subnets: subnets to create ELB in
        :param private_subnets: subnets to autoscale instances in
        :param minsize: minimum size of autoscaling group
        :param maxsize: maximum size of autoscaling group
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param image_id: AWS ami id to create instances from, e.g. 'ami-12345'
        :param instance_type: Instance type to create instances of e.g. 't2.micro' or 't2.nano'
        :param userdata: Instance boot script
        :param service_role_arn: AWS IAM Role with Code Deploy permissions
        :param nat: nat instance for outbound traffic
        :param jump: jump instance for inbound ssh
        :param hosted_zone_name: Route53 hosted zone name string for Route53 record sets
        """
        super(Unit, self).__init__()
        self.template = kwargs['template']
        self.public_cidr = ('PublicIp', '0.0.0.0/0')
        self.elb = Elb(
            vpc=kwargs['vpc'],
            title=kwargs['title'],
            template=self.template,
            protocol=kwargs['protocol'],
            port=kwargs['port'],
            path2ping=kwargs['path2ping'],
            subnets=kwargs['public_subnets'],
            hosted_zone_name=kwargs['hosted_zone_name']
        )
        self.asg = Asg(
            vpc=kwargs['vpc'],
            title=kwargs['title'],
            template=self.template,
            subnets=kwargs['private_subnets'],
            minsize=kwargs['minsize'],
            maxsize=kwargs['maxsize'],
            keypair=kwargs['keypair'],
            image_id=kwargs['image_id'],
            instance_type=kwargs['instance_type'],
            health_check_grace_period=kwargs['health_check_grace_period'],
            health_check_type=kwargs['health_check_type'],
            userdata=kwargs['userdata'],
            load_balancer=self.elb.elb,
            service_role_arn=kwargs['service_role_arn'],
        )
        [self.elb.add_ingress(sender=self.public_cidr, port=port) for port in ['80', '443']]
        self.elb.add_flow(receiver=self.asg, port=kwargs['port'])
        self.asg.add_flow(receiver=kwargs['nat'], port='80')
        self.asg.add_flow(receiver=kwargs['nat'], port='443')
        kwargs['jump'].add_flow(receiver=self.asg, port='22')

    def add_unit_flow(self, receiver, port):
        """
        Create security group flow from this Amazonia unit's ASG to another unit's ELB
        :param receiver: Other Amazonia Unit
        :param port: port for webserver and ELB to communicate via
        """
        self.asg.add_flow(receiver=receiver.elb, port=port)
