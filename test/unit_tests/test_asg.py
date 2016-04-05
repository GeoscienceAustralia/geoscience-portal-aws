import troposphere.elasticloadbalancing as elb
from nose.tools import *
from troposphere import ec2, Ref, Template

from amazonia.classes.asg import Asg

userdata = vpc = subnet = template = load_balancer = None


def setup_resources():
    global userdata, vpc, subnet, template, load_balancer
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


@with_setup(setup_resources())
def test_asg():
    """
    Tests correct structure of autoscaling group objects.
    :return: Pass
    """
    asg_titles = ['simple', 'hard', 'harder', 'easy']

    for title in asg_titles:
        asg = create_asg(title=title)
        assert_equals(asg.asg.title, title + 'Asg')
        assert_equals(asg.asg.MinSize, 1)
        assert_equals(asg.asg.MaxSize, 1)
        assert_equals(asg.asg.VPCZoneIdentifier, [subnet])
        assert_equals(asg.asg.AvailabilityZones, ['ap-southeast-2a'])
        assert_equals(asg.asg.LoadBalancerNames, ['testElb'])
        assert_equals(asg.asg.HealthCheckType, 'ELB')
        assert_equals(asg.asg.HealthCheckGracePeriod, 300)
        assert_equals(asg.lc.title, title + 'Asg' + 'Lc')
        assert_equals(asg.lc.ImageId, 'ami-893f53b3')
        assert_equals(asg.lc.InstanceType, 't2.nano')
        assert_equals(asg.lc.KeyName, 'pipeline')
        assert_equals(asg.lc.SecurityGroups, [asg.security_group.name])
        assert_equals(asg.cd_app.title, title + 'Asg' + 'Cda')
        assert_equals(asg.cd_app.ApplicationName, title + 'Asg')
        assert_equals(asg.cd_deploygroup.title, title + 'Asg' + 'Cdg')
        assert_equals(asg.cd_deploygroup.AutoScalingGroups, [title + 'Asg'])
        assert_equals(asg.cd_deploygroup.ServiceRoleArn, 'instance-iam-role-InstanceProfile-OGL42SZSIQRK')


def create_asg(**kwargs):
    """
    Helper function to create ASG Troposhpere object.
    :return: Troposphere object for single instance, security group and output
    """
    global userdata, vpc, subnet, template, load_balancer

    asg = Asg(title=kwargs['title'],
              keypair='pipeline',
              image_id='ami-893f53b3',
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
    return asg
