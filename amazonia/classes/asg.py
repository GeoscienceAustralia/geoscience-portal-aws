#!/usr/bin/python3

from troposphere import Base64, codedeploy
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration

from amazonia.classes.securityenabledobject import SecurityEnabledObject


class Asg(SecurityEnabledObject):
    def __init__(self, **kwargs):
        """
        Create a an autoscaling group and codedeploy definition
        :param title: Title of the autoscaling application e.g 'webApp1', 'api2' or 'dataprocessing'
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param stack: Troposphere stack to append resources to
        :param minsize: minimum size of autoscaling group
        :param maxsize: maximum size of autoscaling group
        :param subnets: subnets to create autoscaled instances in
        :param load_balancer: load balancer to associate autoscaling group with
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param image_id: AWS ami id to create instances from, e.g. 'ami-12345'
        :param instance_type: Instance type to create instances of e.g. 't2.micro' or 't2.nano'
        :param userdata: Instance boot script
        :param service_role_arn: AWS IAM Role with Code Deploy permissions
        """
        super(Asg, self).__init__(vpc=kwargs['vpc'], title=kwargs['title'], stack=kwargs['stack'])
        self.asg = None
        self.lc = None
        self.cd_app = None
        self.cd_deploygroup = None
        self.add_asg(
            title=kwargs['title'],
            minsize=kwargs['minsize'],
            maxsize=kwargs['maxsize'],
            subnets=kwargs['subnets'],
            load_balancer=kwargs['load_balancer'],
            keypair=kwargs['keypair'],
            image_id=kwargs['image_id'],
            instance_type=kwargs['instance_type'],
            userdata=kwargs['userdata'],
        )
        self.add_cd_deploygroup(
            title=kwargs['title'],
            service_role_arn=kwargs['service_role_arn'],
        )

    def add_asg(self, **kwargs):
        """
        Create autoscaling group object
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/autoscaling.py
        :param title: Title of the autoscaling application
        :param minsize: minimum size of autoscaling group
        :param maxsize: maximum size of autoscaling group
        :param subnets: subnets to create autoscaled instances in
        :param load_balancer: load balancer to associate autoscaling group with
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param image_id: AWS ami id to create instances from, e.g. 'ami-12345'
        :param instance_type: Instance type to create instances of e.g. 't2.micro' or 't2.nano'
        :param userdata: Instance boot script
        """
        asg_title = kwargs['title'] + 'ASG'
        availability_zones = [subnet.AvailabilityZone for subnet in kwargs['subnets']]
        self.asg = self.stack.add_resource(AutoScalingGroup(
            asg_title,
            MinSize=kwargs['minsize'],
            MaxSize=kwargs['maxsize'],
            VPCZoneIdentifier=kwargs['subnets'],
            AvailabilityZones=availability_zones,
            LoadBalancerNames=[kwargs['load_balancer'].title],
        )
        )
        self.asg.LaunchConfigurationName = self.add_launch_config(
            title=kwargs['title'],
            keypair=kwargs['keypair'],
            image_id=kwargs['image_id'],
            instance_type=kwargs['instance_type'],
            userdata=kwargs['userdata'],
        )
        self.asg.HealthCheckType = 'ELB'
        self.asg.HealthCheckGracePeriod = 300

    def add_launch_config(self, **kwargs):
        """
        Method to add a launch configuration resource to a cloud formation document
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/autoscaling.py
        :param title: Title of the autoscaling application
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param image_id: AWS ami id to create instances from, e.g. 'ami-12345'
        :param instance_type: Instance type to create instances of e.g. 't2.micro' or 't2.nano'
        :param userdata: Instance boot script
        :return string representing Launch Configuration name
        """
        launch_config_title = kwargs['title'] + 'LC'

        self.lc = self.stack.add_resource(LaunchConfiguration(
            kwargs['launch_config_title'],
            AssociatePublicIpAddress=False,
            ImageId=kwargs['image_id'],
            InstanceMonitoring=False,
            InstanceType=kwargs['instance_type'],
            KeyName=kwargs['keypair'],
            SecurityGroups=[self.security_group.name],
        ))
        self.lc.UserData = Base64(kwargs['userdata'])
        return launch_config_title

    def add_cd_deploygroup(self, **kwargs):
        """
        Create CodeDeploy application and deploy group  and associate with auto scaling group
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/codedeploy.py
        :param title: Title of the code deploy application
        :param service_role_arn: AWS IAM Role with Code Deploy permissions
        """
        cd_app_title = kwargs['title'] + 'CDA'
        cd_deploygroup_title = kwargs['title'] + 'CDG'

        self.cd_app = self.stack.add_resource(codedeploy.Application(cd_app_title,
                                                                     ApplicationName=title))
        self.cd_deploygroup = self.stack.add_resource(
            codedeploy.DeploymentGroup(cd_deploygroup_title,
                                       ApplicationName=self.cd_app.title,
                                       AutoScalingGroups=[self.asg.title],
                                       DeploymentConfigName='CodeDeployDefault.OneAtATime',
                                       DeploymentGroupName=cd_deploygroup_title,
                                       ServiceRoleArn=kwargs['service_role_arn']))
        self.cd_deploygroup.DependsOn = [self.cd_app.title, self.asg.title]
