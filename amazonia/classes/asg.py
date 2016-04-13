#!/usr/bin/python3

from troposphere import Base64, codedeploy, Ref, Join
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration, Tag

from amazonia.classes.securityenabledobject import SecurityEnabledObject


class Asg(SecurityEnabledObject):
    def __init__(self, title, vpc, template, minsize, maxsize, subnets, load_balancer,
                 keypair, image_id, instance_type, userdata, service_role_arn):
        """
        Creates an autoscaling group and codedeploy definition
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
        super(Asg, self).__init__(vpc=vpc, title=title, template=template)
        if maxsize < minsize:
            print("Error: minsize must be lower than maxsize.")
            print("Error: minsize {0}".format(minsize))
            print("Error: maxsize {0}".format(maxsize))
            exit(1)

        self.template = template
        self.title = title + 'Asg'
        self.trop_asg = None
        self.lc = None
        self.cd_app = None
        self.cd_deploygroup = None
        self.create_asg(
            self.title,
            minsize,
            maxsize,
            subnets,
            load_balancer,
            keypair,
            image_id,
            instance_type,
            userdata
        )
        self.create_cd_deploygroup(
            self.title,
            service_role_arn
        )

    def create_asg(self, title, minsize, maxsize, subnets, load_balancer, keypair, image_id, instance_type, userdata):
        """
        Creates an autoscaling group object
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
        :return string representing Auto Scaling Group name
        """
        availability_zones = [subnet.AvailabilityZone for subnet in subnets]
        self.trop_asg = self.template.add_resource(AutoScalingGroup(
            title,
            MinSize=minsize,
            MaxSize=maxsize,
            VPCZoneIdentifier=[Ref(subnet.title) for subnet in subnets],
            AvailabilityZones=availability_zones,
            LoadBalancerNames=[Ref(load_balancer)],
            Tags=[Tag('Name', Join('', [Ref('AWS::StackName'), '-', title]), True)]
        )
        )
        self.trop_asg.LaunchConfigurationName = Ref(self.create_launch_config(
            title,
            keypair,
            image_id,
            instance_type,
            userdata
        ))
        self.trop_asg.HealthCheckType = 'ELB'
        self.trop_asg.HealthCheckGracePeriod = 300
        return title

    def create_launch_config(self, title, keypair, image_id, instance_type, userdata):
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
        launch_config_title = title + 'Lc'

        self.lc = self.template.add_resource(LaunchConfiguration(
            launch_config_title,
            AssociatePublicIpAddress=False,
            ImageId=image_id,
            InstanceMonitoring=False,
            InstanceType=instance_type,
            KeyName=keypair,
            SecurityGroups=[Ref(self.security_group.name)],
        ))
        self.lc.UserData = Base64(userdata)
        return launch_config_title

    def create_cd_deploygroup(self, title, service_role_arn):
        """
        Creates a CodeDeploy application and deploy group and associates with autoscaling group
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/codedeploy.py
        :param title: Title of the code deploy application
        :param service_role_arn: AWS IAM Role with Code Deploy permissions
        :return 2 strings representing CodeDeploy Application name and CodeDeploy Group name.
        """
        cd_app_title = title + 'Cda'
        cd_deploygroup_title = title + 'Cdg'

        self.cd_app = self.template.add_resource(codedeploy.Application(cd_app_title,
                                                                        ApplicationName=Join('', [Ref('AWS::StackName'),
                                                                                                  '-', cd_app_title])))
        self.cd_deploygroup = self.template.add_resource(
            codedeploy.DeploymentGroup(cd_deploygroup_title,
                                       ApplicationName=Ref(self.cd_app),
                                       AutoScalingGroups=[Ref(self.trop_asg)],
                                       DeploymentConfigName='CodeDeployDefault.OneAtATime',
                                       DeploymentGroupName=Join('', [Ref('AWS::StackName'),
                                                                     '-', cd_deploygroup_title]),
                                       ServiceRoleArn=service_role_arn))
        self.cd_deploygroup.DependsOn = [self.cd_app.title, self.trop_asg.title]
        return cd_app_title, cd_deploygroup_title
