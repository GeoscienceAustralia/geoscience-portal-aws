import troposphere.elasticloadbalancing as elb
from nose.tools import *
from troposphere import ec2, Ref, Template, Join

from amazonia.classes.asg import Asg

userdata = vpc = subnet = template = load_balancer = health_check_grace_period = health_check_type = None


def setup_resources():
    global userdata, vpc, subnet, template, load_balancer, health_check_grace_period, health_check_type
    template = Template()
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

    load_balancer = elb.LoadBalancer('testElb',
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

    health_check_grace_period = 300
    health_check_type = 'ELB'


@with_setup(setup_resources())
def test_asg():
    """
    Tests correct structure of autoscaling group objects.
    :return: Pass
    """
    asg_titles = ['simple', 'hard', 'harder', 'easy']

    for title in asg_titles:
        asg = create_asg(title)
        assert_equals(asg.trop_asg.title, title + 'Asg')
        assert_equals(asg.trop_asg.MinSize, 1)
        assert_equals(asg.trop_asg.MaxSize, 1)
        [assert_is(type(subnet_id), Ref) for subnet_id in asg.trop_asg.VPCZoneIdentifier]
        assert_is(type(asg.trop_asg.LaunchConfigurationName), Ref)
        assert_equals(asg.trop_asg.AvailabilityZones, ['ap-southeast-2a'])
        [assert_is(type(lbn), Ref) for lbn in asg.trop_asg.LoadBalancerNames]
        assert_equals(asg.trop_asg.HealthCheckType, 'ELB')
        assert_equals(asg.trop_asg.HealthCheckGracePeriod, 300)
        assert_equals(asg.lc.title, title + 'Asg' + 'Lc')
        assert_equals(asg.lc.ImageId, 'ami-162c0c75')
        assert_equals(asg.lc.InstanceType, 't2.nano')
        assert_equals(asg.lc.KeyName, 'pipeline')
        [assert_is(type(sg), Ref) for sg in asg.lc.SecurityGroups]
        assert_equals(asg.cd_app.title, title + 'Asg' + 'Cda')
        assert_is(type(asg.cd_app.ApplicationName), Join)
        assert_is(type(asg.cd_deploygroup.ApplicationName), Ref)
        assert_equals(asg.cd_deploygroup.title, title + 'Asg' + 'Cdg')
        assert_is(type(asg.cd_deploygroup.DeploymentGroupName), Join)
        [assert_is(type(cdasg), Ref) for cdasg in asg.cd_deploygroup.AutoScalingGroups]
        assert_equals(asg.cd_deploygroup.ServiceRoleArn, 'arn:aws:iam::658691668407:role/CodeDeployServiceRole')


def create_asg(title):
    """
    Helper function to create ASG Troposhpere object.
    :return: Troposphere object for single instance, security group and output
    """
    global userdata, vpc, subnet, template, load_balancer, health_check_grace_period, health_check_type
    asg = Asg(
        title=title,
        vpc=vpc,
        template=template,
        minsize=1,
        maxsize=1,
        subnets=[subnet],
        load_balancer=load_balancer,
        keypair='pipeline',
        image_id='ami-f2210191',
        instance_type='t2.micro',
        health_check_grace_period=health_check_grace_period,
        health_check_type=health_check_type,
        userdata=userdata,
        service_role_arn='arn:aws:iam::658691668407:role/CodeDeployServiceRole'
    )

    return asg
