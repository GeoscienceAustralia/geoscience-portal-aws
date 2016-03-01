#!/usr/bin/env python

# pylint: disable=missing-docstring, invalid-name, line-too-long, redefined-outer-name, too-many-arguments

from amazonia.cftemplates import SingleAZenv
from amazonia.amazonia_resources import *

def main():
    keypair = "Your Keypair name Here"
    template = SingleAZenv(keypair)
    HTTP_PORT="80"      # This variable is used to specify the port for general HTTP traffic
    HTTPS_PORT="443"    # This variable is used to specify the port for general HTTPS traffic
    APP_PORT="8080"     # This variable is used to specify App specific port (eg. 8080 is commonly used in many apps)

    elb_sg = add_security_group(template, template.vpc)
    web_sg = add_security_group(template, template.vpc)

    # NAT Rules
    # all from web security group
    # all to public
    add_security_group_ingress(template, template.nat_sg, "-1", "-1", "-1", source_security_group=web_sg)
    add_security_group_egress(template, template.nat_sg, "-1", "-1", "-1", cidr=PUBLIC_CIDR)

    # ELB Rules
    # 80 and 443 from public
    # all to public
    add_security_group_ingress(template, elb_sg, "tcp", HTTP_PORT, HTTP_PORT, cidr=PUBLIC_CIDR)
    add_security_group_ingress(template, elb_sg, "tcp", HTTPS_PORT, HTTPS_PORT, cidr=PUBLIC_CIDR)
    add_security_group_egress(template, elb_sg, "-1", "-1", "-1", destination_security_group=web_sg)

    # WEB Rules
    # 80, 443, and 8080 from ELB security group
    # all to NAT security group
    add_security_group_ingress(template, web_sg, "tcp", HTTP_PORT, HTTP_PORT, source_security_group=elb_sg)
    add_security_group_ingress(template, web_sg, "tcp", APP_PORT, APP_PORT, source_security_group=elb_sg)
    add_security_group_ingress(template, web_sg, "tcp", HTTPS_PORT, HTTPS_PORT, source_security_group=elb_sg)
    add_security_group_egress(template, web_sg, "-1", "-1", "-1", destination_security_group=template.nat_sg)

    #elb = add_load_balancer(template, [template.public_subnet], 'HTTP:8080/error/noindex.html', [elb_sg])
    elb = add_load_balancer(template, [template.public_subnet], 'HTTP:8080/error/noindex.html', [elb_sg], 
             loadbalancerport = "443"   , protocol          = "HTTPS", 
             instanceport     = "8080"  , instanceprotocol  = "HTTP")    

    web_launch_config = add_launch_config(template, keypair, [web_sg], WEB_IMAGE_ID, WEB_INSTANCE_TYPE, userdata=WEB_SERVER_AZ1_USER_DATA)
    web_launch_config.AssociatePublicIpAddress = False
    web_asg = add_auto_scaling_group(template, 1, [template.private_subnet], launch_configuration=web_launch_config, health_check_type="ELB", load_balancer=elb, dependson=[template.internet_gateway.title])

    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
