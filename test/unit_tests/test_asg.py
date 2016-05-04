import troposphere.elasticloadbalancing as elb
from nose.tools import *
from troposphere import ec2, Ref, Template, Join

from amazonia.classes.asg import Asg, MinMaxError

userdata = vpc = subnet = template = load_balancer = health_check_grace_period = health_check_type = \
    cd_service_role_arn = instance_type = image_id = keypair = iam_instance_profile_arn = None


def setup_resources():
    """
    Initialise resources before each test
    """
    global userdata, vpc, subnet, template, load_balancer, health_check_grace_period, health_check_type, \
        cd_service_role_arn, instance_type, image_id, keypair, iam_instance_profile_arn
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
    cd_service_role_arn = 'arn:aws:iam::658691668407:role/CodeDeployServiceRole'
    iam_instance_profile_arn = 'arn:aws:iam::12345678987654321:role/InstanceProfileRole'
    image_id = 'ami-05446966'
    instance_type = 't2.micro'
    keypair = 'pipeline'


@with_setup(setup_resources())
def test_asg():
    """
    Tests correct structure of autoscaling group objects.
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
        assert_equals(asg.lc.ImageId, 'ami-05446966')
        assert_equals(asg.lc.InstanceType, 't2.micro')
        assert_equals(asg.lc.KeyName, 'pipeline')
        assert_equals(asg.lc.IamInstanceProfile, 'arn:aws:iam::12345678987654321:role/InstanceProfileRole')
        [assert_is(type(sg), Ref) for sg in asg.lc.SecurityGroups]
        assert_equals(asg.cd_app.title, title + 'Asg' + 'Cda')
        assert_is(type(asg.cd_app.ApplicationName), Join)
        assert_is(type(asg.cd_deploygroup.ApplicationName), Ref)
        assert_equals(asg.cd_deploygroup.title, title + 'Asg' + 'Cdg')
        assert_is(type(asg.cd_deploygroup.DeploymentGroupName), Join)
        [assert_is(type(cdasg), Ref) for cdasg in asg.cd_deploygroup.AutoScalingGroups]
        assert_equals(asg.cd_deploygroup.ServiceRoleArn, 'arn:aws:iam::658691668407:role/CodeDeployServiceRole')


@with_setup(setup_resources())
def test_min_gtr_max_error():
    """
    Tests that a higher minsize than maxsize is detected and raises an error.
    """
    global userdata, vpc, subnet, template, load_balancer, health_check_grace_period, health_check_type, \
        cd_service_role_arn, image_id, instance_type, keypair

    assert_raises(MinMaxError, Asg, **{'title': 'test',
                                       'vpc': vpc,
                                       'template': template,
                                       'minsize': 2,
                                       'maxsize': 1,
                                       'subnets': [subnet],
                                       'load_balancer': load_balancer,
                                       'keypair': keypair,
                                       'image_id': image_id,
                                       'instance_type': instance_type,
                                       'health_check_grace_period': health_check_grace_period,
                                       'health_check_type': health_check_type,
                                       'userdata': userdata,
                                       'cd_service_role_arn': None,
                                       'iam_instance_profile_arn': None
    })


@with_setup(setup_resources())
def test_no_cd_group():
    """
    Test that an asg is created without a CD when a null code deploy roles is passed in
    """
    global userdata, vpc, subnet, template, load_balancer, health_check_grace_period, health_check_type, \
        cd_service_role_arn, image_id, instance_type, keypair
    asg = Asg(
        title='noCd',
        vpc=vpc,
        template=template,
        minsize=1,
        maxsize=1,
        subnets=[subnet],
        load_balancer=load_balancer,
        keypair=keypair,
        image_id=image_id,
        instance_type=instance_type,
        health_check_grace_period=health_check_grace_period,
        health_check_type=health_check_type,
        userdata=userdata,
        cd_service_role_arn=None,
        iam_instance_profile_arn=None
    )
    assert_equals(asg.cd_app, None)
    assert_equals(asg.cd_deploygroup, None)


def create_asg(title):
    """
    Helper function to create ASG Troposhpere object.
    :return: Troposphere object for single instance, security group and output
    """
    global userdata, vpc, subnet, template, load_balancer, health_check_grace_period, health_check_type, \
        cd_service_role_arn, image_id, instance_type, keypair, iam_instance_profile_arn
    asg = Asg(
        title=title,
        vpc=vpc,
        template=template,
        minsize=1,
        maxsize=1,
        subnets=[subnet],
        load_balancer=load_balancer,
        keypair=keypair,
        image_id=image_id,
        instance_type=instance_type,
        health_check_grace_period=health_check_grace_period,
        health_check_type=health_check_type,
        userdata=userdata,
        cd_service_role_arn=cd_service_role_arn,
        iam_instance_profile_arn=iam_instance_profile_arn
    )

    return asg
