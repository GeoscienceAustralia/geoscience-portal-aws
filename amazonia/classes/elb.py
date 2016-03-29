#!/usr/bin/python3

from amazonia.amazonia_resources import *


class Elb(SecurityEnabledObject):
    def __init__(self, **kwargs):
        """ Public Class to create a Triple AZ environment in a vpc """
        super(SecurityEnabledObject, self).__init__()

        return_elb = template.add_resource(
            elb.LoadBalancer(elb_title,
                             CrossZone=True,
                             HealthCheck=elb.HealthCheck(Target=healthcheck_target,
                                                         HealthyThreshold="2",
                                                         UnhealthyThreshold="5",
                                                         Interval="15",
                                                         Timeout="5"),
                             Listeners=[elb.Listener(LoadBalancerPort=loadbalancerport,
                                                     Protocol=protocol,
                                                     InstancePort=instanceport,
                                                     InstanceProtocol=instanceprotocol)],
                             Scheme="internet-facing",
                             SecurityGroups=[isCfObject(x) for x in security_groups],
                             Subnets=[isCfObject(x) for x in subnets],
                             Tags=Tags(Name=name_tag(elb_title))))


        # TODO Elb Unit Tests:
        # TODO Unit Tests:jump_sg = jumphost1.NetworkInterfaces.GroupSet,
        # TODO Sys Tests: Connect from jumphost to subpub1 instance, subpub2 instance, can't connect on port 80,8080,443
        # TODO Sys Tests: Try connecting to host in another vpc

