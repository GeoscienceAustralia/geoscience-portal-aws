#!/usr/bin/env python

from amazonia.classes.elb import Elb
from troposphere import ec2, Ref


def main():

    vpc = ec2.VPC('MyVPC',
                  CidrBlock='10.0.0.0/16')
    pub_sub_list = [ec2.Subnet('MyPubSub1',
                        AvailabilityZone='ap-southeast-2a',
                        VpcId=Ref(vpc),
                        CidrBlock='10.0.1.0/24'),
                    ec2.Subnet('MyPubSub2',
                               AvailabilityZone='ap-southeast-2b',
                               VpcId=Ref(vpc),
                               CidrBlock='10.0.2.0/24'),
                    ec2.Subnet('MyPubSub3',
                               AvailabilityZone='ap-southeast-2c',
                               VpcId=Ref(vpc),
                               CidrBlock='10.0.3.0/24')
                    ]

    template = Elb(title='elb',
                   port='80',
                   subnets=pub_sub_list,
                   protocol='t2.nano')

    template.add_resource(vpc)
    template.add_resource(subnet)
    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
