#!/usr/bin/env python

from troposphere import Template
from amazonia.amazonia_resources import *


def main():
    template = Template()
    vpc = add_vpc(template, VPC_CIDR)

    r53_hosted_zone = add_r53_hosted_zone(template, vpc)
    num_r53_record_set = add_r53_record_set(template, r53_hosted_zone, "testdns", "10.0.0.4", "A")
    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
