#!/usr/bin/env python

from troposphere import Template
from amazonia.amazonia_resources import *


def main():
    template = Template()
    vpc = add_vpc(template, VPC_CIDR)
    db_port = 5432

    sub1 = add_subnet(template, vpc, "subnet", PUBLIC_SUBNET_AZ1_CIDR)
    sub1.AvailabilityZone = AVAILABILITY_ZONES[0]

    sub2 = add_subnet(template, vpc, "subnet", PUBLIC_SUBNET_AZ2_CIDR)
    sub2.AvailabilityZone = AVAILABILITY_ZONES[1]

    raw_subnets = [sub1, sub2]

    db_subnet_group = add_db_subnet_group(template, raw_subnets)
    db_security_group = add_security_group(template, vpc)
    add_security_group_ingress(template, db_security_group, "tcp", db_port, db_port)

    add_db(template, "postgres", db_subnet_group, "username", "password", db_security_groups=db_security_group, db_port=db_port)

    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
