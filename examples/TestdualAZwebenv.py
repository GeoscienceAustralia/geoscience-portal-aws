#!/usr/bin/env python

# pylint: disable=missing-docstring, invalid-name, line-too-long, redefined-outer-name, too-many-arguments

from amazonia.cftemplates import Template
from amazonia.amazonia_resources import *

def main():
    keypair = "aera"
    template = Template()
    HTTP_PORT="80"      # This variable is used to specify the port for general HTTP traffic
    HTTPS_PORT="443"    # This variable is used to specify the port for general HTTPS traffic
    APP_PORT="8080"     # This variable is used to specify App specific port (eg. 8080 is commonly used in many apps)
    PUBLIC_CIDR = "0.0.0.0/0"
    nat_security_group = "sg-f4796691"
    vpc = "vpc-4a6e0c2f"
    elb_sg = add_security_group(template, vpc)
    web_sg = add_security_group(template, vpc)

    # NAT Rules
    # all from web security group
    # all to public
    add_security_group_ingress(template, nat_security_group, "-1", "-1", "-1", source_security_group=web_sg)
    add_security_group_egress(template, nat_security_group, "-1", "-1", "-1", cidr=PUBLIC_CIDR)

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
    add_security_group_egress(template, web_sg, "-1", "-1", "-1", destination_security_group=nat_security_group)

    web1 = add_web_instance(template, keypair, "subnet-a39bcfc6", web_sg, WEB_SERVER_AZ1_USER_DATA, public=False)
    web2 = add_web_instance(template, keypair, "subnet-993449ee", web_sg, WEB_SERVER_AZ2_USER_DATA, public=False)
    #
    elb = add_load_balancer(template, ["subnet-a29bcfc7", "subnet-853449f2"], 'HTTP:8080/error/noindex.html', [elb_sg], resources=[web1, web2])

    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
