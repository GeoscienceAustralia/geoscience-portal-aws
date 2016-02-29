#!/usr/bin/env python

from troposphere import Template
from amazonia.amazonia_resources import *


def main():
    template = Template()
    vpc = "vpc-b26f0cd7"
    db_port = 5432
    raw_subnets = ["subnet-d396c3b6", "subnet-99cdbeee"]
    db_subnet_group = add_db_subnet_group(template, raw_subnets)
    db_security_group = add_security_group(template, vpc)
    add_security_group_ingress(template, db_security_group, "tcp", db_port, db_port)

    my_hiera_client =  hiera.HieraClient(hiera_file, hiera_path=hiera_directory, application='my_app_name')

    username = my_hiera_client.get('my_app_name::rds_user')
    password = my_hiera_client.get('my_app_name::rds_password')

    add_db(template, "postgres", db_subnet_group, username, password, db_security_groups=db_security_group, db_port=db_port)

    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
