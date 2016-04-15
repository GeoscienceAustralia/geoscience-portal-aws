#!/usr/bin/python3

from troposphere import Base64, codedeploy, Ref, Join
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration, Tag

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
        self.title = kwargs['title'] + 'Asg'
        super(Asg, self).__init__(vpc=kwargs['vpc'], title=self.title, template=kwargs['template'])
        self.asg = None
        self.lc = None
        self.cd_app = None
        self.cd_deploygroup = None
        self.add_asg(
            title=self.title,
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
            title=self.title,
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
        availability_zones = [subnet.AvailabilityZone for subnet in kwargs['subnets']]
        self.asg = self.template.add_resource(AutoScalingGroup(
            kwargs['title'],
            MinSize=kwargs['minsize'],
            MaxSize=kwargs['maxsize'],
            VPCZoneIdentifier=[Ref(subnet.title) for subnet in kwargs['subnets']],
            AvailabilityZones=availability_zones,
            LoadBalancerNames=[Ref(kwargs['load_balancer'])],
            Tags=[Tag('Name', Join('', [Ref('AWS::StackName'), '-', kwargs['title']]), True)]
        )
        )
        self.asg.LaunchConfigurationName = Ref(self.add_launch_config(
            title=kwargs['title'],
            keypair=kwargs['keypair'],
            image_id=kwargs['image_id'],
            instance_type=kwargs['instance_type'],
            userdata=kwargs['userdata'],
        ))
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
        launch_config_title = kwargs['title'] + 'Lc'

        self.lc = self.template.add_resource(LaunchConfiguration(
            launch_config_title,
            AssociatePublicIpAddress=False,
            ImageId=kwargs['image_id'],
            InstanceMonitoring=False,
            InstanceType=kwargs['instance_type'],
            KeyName=kwargs['keypair'],
            SecurityGroups=[Ref(self.security_group.name)],
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
        cd_app_title = kwargs['title'] + 'Cda'
        cd_deploygroup_title = kwargs['title'] + 'Cdg'

        self.cd_app = self.template.add_resource(codedeploy.Application(cd_app_title,
                                                                        ApplicationName=Join('', [Ref('AWS::StackName'),
                                                                                                  '-', cd_app_title])))
        self.cd_deploygroup = self.template.add_resource(
            codedeploy.DeploymentGroup(cd_deploygroup_title,
                                       ApplicationName=Ref(self.cd_app),
                                       AutoScalingGroups=[Ref(self.asg)],
                                       DeploymentConfigName='CodeDeployDefault.OneAtATime',
                                       DeploymentGroupName=Join('', [Ref('AWS::StackName'),
                                                                     '-', cd_deploygroup_title]),
                                       ServiceRoleArn=kwargs['service_role_arn']))
        self.cd_deploygroup.DependsOn = [self.cd_app.title, self.asg.title]
