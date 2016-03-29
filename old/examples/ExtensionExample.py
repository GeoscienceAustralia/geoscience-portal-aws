#!/usr/bin/env python

# pylint: disable=missing-docstring, invalid-name, line-too-long, redefined-outer-name, too-many-arguments

from amazonia.cftemplates import DualAZenv
from amazonia.amazonia_resources import *

def main():
    keypair = "Your Keypair name Here"
    template = DualAZenv(keypair)
    HTTP_PORT="80"      # This variable is used to specify the port for general HTTP traffic
    HTTPS_PORT="443"    # This variable is used to specify the port for general HTTPS traffic
    APP_PORT="8080"     # This variable is used to specify App specific port (eg. 8080 is commonly used instead of 80 in many apps)
    SSH_PORT="22"       # This variable is used to specify the port for ssh traffic.

    elb_sg = add_security_group(template, template.vpc)
    web_sg = add_security_group(template, template.vpc)

    # NAT Rules
    # all from web security group
    # all to public
    add_security_group_ingress(template, template.nat_security_group, "-1", "-1", "-1", source_security_group=web_sg)
    add_security_group_ingress(template, template.nat_security_group, "tcp", SSH_PORT, SSH_PORT,  cidr=PUBLIC_COMPANY_CIDR)
    add_security_group_egress(template, template.nat_security_group, "-1", "-1", "-1", cidr=PUBLIC_CIDR)

    # ELB Rules
    # 80 and 443 from public
    # all to public
    add_security_group_ingress(template, elb_sg, "tcp", HTTP_PORT, HTTP_PORT, cidr=PUBLIC_CIDR)
    add_security_group_ingress(template, elb_sg, "tcp", HTTPS_PORT, HTTPS_PORT, cidr=PUBLIC_CIDR)
    add_security_group_egress(template, elb_sg, "-1", "-1", "-1", destination_security_group=web_sg)

    # WEB Rules
    # 80, 443, and 8080 from ELB security group
    # all to NAT security group
    add_security_group_ingress(template, web_sg, "tcp", SSH_PORT, SSH_PORT, source_security_group=template.nat_security_group)
    add_security_group_ingress(template, web_sg, "tcp", HTTP_PORT, HTTP_PORT, source_security_group=elb_sg)
    add_security_group_ingress(template, web_sg, "tcp", APP_PORT, APP_PORT, source_security_group=elb_sg)
    add_security_group_ingress(template, web_sg, "tcp", HTTPS_PORT, HTTPS_PORT, source_security_group=elb_sg)
    add_security_group_egress(template, web_sg, "-1", "-1", "-1", destination_security_group=template.nat_security_group)

    # Add 2 web instances using the amazonia function (troposphere can be used here if preferred)
    web1 = add_web_instance(template, keypair, template.private_subnet1, web_sg, WEB_SERVER_AZ1_USER_DATA, public=False)
    web2 = add_web_instance(template, keypair, template.private_subnet2, web_sg, WEB_SERVER_AZ2_USER_DATA, public=False)

    # The below is an example of using troposphere to extend the web instances that are returned via the amazonia function.
    # NOTE: The DeviceName here can be the root device (as we've used in this case) to increase the capacity of the root device.
    #       Or a different device name can be specified to attempt to add a secondary drive to your instance.
    web1.BlockDeviceMappings = [ec2.BlockDeviceMapping(DeviceName="/dev/xvda", Ebs=ec2.EBSBlockDevice(VolumeSize="40", VolumeType="gp2", DeleteOnTermination="true"))]
    web2.BlockDeviceMappings = [ec2.BlockDeviceMapping(DeviceName="/dev/xvda", Ebs=ec2.EBSBlockDevice(VolumeSize="40", VolumeType="gp2", DeleteOnTermination="true"))]

    elb = add_load_balancer(template, [template.public_subnet1, template.public_subnet2], 'HTTP:8080/error/noindex.html', [elb_sg], resources=[web1, web2])

    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
