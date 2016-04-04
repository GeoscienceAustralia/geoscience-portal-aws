#!/usr/bin/python3

from amazonia.classes.subnet import Subnet
from troposphere import ec2, Ref, Template


def main():
    stack = Template()
    az_b = 'ap-southeast-2b'
    az_c = 'ap-southeast-2c'
    stack.private_subnets = ['PrivateSubnetA']
    stack.public_subnets = ['PublicSubnetA', 'PublicSubnetA']

    stack.vpc = stack.add_resource(ec2.VPC('MyVPC',
                                           CidrBlock='10.0.0.0/16'))
    stack.public_route_table = stack.add_resource(ec2.RouteTable('MyUnitPublicRouteTable',
                                                              VpcId=Ref(stack.vpc)))
    stack.private_route_table = stack.add_resource(ec2.RouteTable('MyUnitPrivateRouteTable',
                                                              VpcId=Ref(stack.vpc)))
    pubsubnet3 = Subnet(stack=stack,
                        route_table=stack.public_route_table,
                        az=az_c)
    prisubnet2 = Subnet(stack=stack,
                        route_table=stack.private_route_table,
                        az=az_b)

    print(stack.to_json(indent=2, separators=(',', ': ')))
if __name__ == "__main__":
    main()
