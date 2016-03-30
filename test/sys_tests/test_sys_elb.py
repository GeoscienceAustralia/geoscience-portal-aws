#!/usr/bin/python3

from amazonia.classes.elb import Elb
from troposphere import ec2, Ref, Tags, Template


def main():

    vpc = ec2.VPC('MyVPC',
                  CidrBlock='10.0.0.0/16')

    internet_gateway = ec2.InternetGateway('MyInternetGateway',
                                           Tags=Tags(Name='MyInternetGateway'))

    internet_gateway_ass = ec2.VPCGatewayAttachment('MyVPCGatewayAttachment',
                                                    InternetGatewayId=Ref(internet_gateway),
                                                    VpcId=Ref(vpc))

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
                               CidrBlock='10.0.3.0/24')]

    elb = Elb(title='elb',
              port='80',
              subnets=pub_sub_list,
              protocol='http',
              vpc=vpc,
              path2ping='index.html',
              stack=Template())

    elb.stack.add_resource(vpc)
    elb.stack.add_resource(internet_gateway)
    elb.stack.add_resource(internet_gateway_ass)
    elb.stack.add_resource(pub_sub_list)
    print(elb.stack.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
