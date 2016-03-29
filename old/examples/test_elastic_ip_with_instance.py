#!/usr/bin/env python

from troposphere import Template
from amazonia.amazonia_resources import *


def main():
    template = Template()
    vpc = add_vpc(template, VPC_CIDR)

    elastic_ip = add_elastic_ip(template, vpc, instance_id="i-5c440b83")

    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
