#!/usr/bin/python3

import troposphere.elasticloadbalancing as elb
from troposphere import ec2, Ref, Template

from amazonia.classes.asg import Asg


def main():
    userdata = """
#cloud-config
repo_update: true
repo_upgrade: all

packages:
 - httpd

runcmd:
 - service httpd start
    """
    vpc = ec2.VPC('MyVPC',
                  CidrBlock='10.0.0.0/16')
    subnet = ec2.Subnet('MySubnet',
                        AvailabilityZone='ap-southeast-2a',
                        VpcId=Ref(vpc),
                        CidrBlock='10.0.1.0/24')

    load_balancer = elb.LoadBalancer('MyELB',
                                     CrossZone=True,
                                     HealthCheck=elb.HealthCheck(Target='HTTP:8080/error/noindex.html',
                                                                 HealthyThreshold='2',
                                                                 UnhealthyThreshold='5',
                                                                 Interval='15',
                                                                 Timeout='5'),
                                     Listeners=[elb.Listener(LoadBalancerPort='80',
                                                             Protocol='HTTP',
                                                             InstancePort='80',
                                                             InstanceProtocol='HTTP')],
                                     Scheme='internet-facing',
                                     Subnets=[subnet])

    template = Template()
    Asg(title='simple',
        keypair='pipeline',
        image_id='ami-162c0c75',
        instance_type='t2.nano',
        vpc=vpc,
        subnets=[subnet],
        availability_zones=['ap-southeast-2a'],
        minsize=1,
        maxsize=1,
        load_balancer=load_balancer,
        userdata=userdata,
        service_role_arn='instance-iam-role-InstanceProfile-OGL42SZSIQRK',
        template=template)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
