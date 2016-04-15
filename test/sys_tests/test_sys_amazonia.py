#!/usr/bin/python3

from amazonia.classes.elb import Elb
from troposphere import ec2, Ref, Tags, Template


def main():
    template = Template()
    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))

    internet_gateway = template.add_resource(ec2.InternetGateway('MyInternetGateway',
                                                                 Tags=Tags(Name='MyInternetGateway')))

    template.add_resource(ec2.VPCGatewayAttachment('MyVPCGatewayAttachment',
                                                   InternetGatewayId=Ref(internet_gateway),
                                                   VpcId=Ref(vpc)))

    public_subnets = [template.add_resource(ec2.Subnet('MyPubSub1',
                                                       AvailabilityZone='ap-southeast-2a',
                                                       VpcId=Ref(vpc),
                                                       CidrBlock='10.0.1.0/24')),
                      template.add_resource(ec2.Subnet('MyPubSub2',
                                                       AvailabilityZone='ap-southeast-2b',
                                                       VpcId=Ref(vpc),
                                                       CidrBlock='10.0.2.0/24')),
                      template.add_resource(ec2.Subnet('MyPubSub3',
                                                       AvailabilityZone='ap-southeast-2c',
                                                       VpcId=Ref(vpc),
                                                       CidrBlock='10.0.3.0/24'))]

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == "__main__":
    main()
