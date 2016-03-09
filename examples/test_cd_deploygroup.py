#!/usr/bin/env python

from troposphere import Template
from amazonia.amazonia_resources import *


def main():
    template = Template()
    vpc = add_vpc(template, VPC_CIDR)

    sub1 = add_subnet(template, vpc, "subnet", PUBLIC_SUBNET_AZ1_CIDR)
    sub1.AvailabilityZone = AVAILABILITY_ZONES[0]

    keypair = "pipeline"
    app_name = "testapp"

    HTTP_PORT = "80"
    userdata = ""
    IAM_INSTANCE_PROFILE = "instance-iam-role-InstanceProfile-OGL42SZSIQRK"

    web_sg = add_security_group(template, vpc)
    add_security_group_ingress(template, web_sg, "tcp", HTTP_PORT, HTTP_PORT, cidr=PUBLIC_SUBNET_AZ1_CIDR)

    web_launch_config = add_launch_config(template, keypair, [web_sg], WEB_IMAGE_ID, WEB_INSTANCE_TYPE, userdata=userdata)
    web_launch_config.IamInstanceProfile = IAM_INSTANCE_PROFILE
    auto_scaling_group = add_auto_scaling_group(template, 1, [sub1], launch_configuration=web_launch_config, app_name=app_name)

    cd_application = add_cd_application(template, app_name=app_name)
    cd_deploygroup = add_cd_deploygroup(template, cd_application, auto_scaling_group, service_role_arn="arn:aws:iam::658691668407:role/CodeDeployServiceRole")

    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
