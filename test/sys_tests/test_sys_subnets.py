#!/usr/bin/python3

from amazonia.classes.subnet import Subnet
from troposphere import ec2, Ref, Template


def main():
    stack = Template()
    az_a = 'ap-southeast-2a'
    az_b = 'ap-southeast-2b'
    az_c = 'ap-southeast-2c'
    stack.pri_sub_list = []
    stack.pub_sub_list = []

    stack.vpc = stack.add_resource(ec2.VPC('MyVPC',
                                           CidrBlock='10.0.0.0/16'))
    stack.pub_route_table = stack.add_resource(ec2.RouteTable('MyUnitPublicRouteTable',
                                                              VpcId=Ref(stack.vpc)))
    stack.pri_route_table = stack.add_resource(ec2.RouteTable('MyUnitPrivateRouteTable',
                                                              VpcId=Ref(stack.vpc)))

    pubsubnet1 = stack.pub_sub_list.append(Subnet(stack=stack,
                        route_table=stack.pub_route_table,
                        az=az_a))
    pubsubnet2 = stack.pub_sub_list.append(Subnet(stack=stack,
                        route_table=stack.pub_route_table,
                        az=az_b))
    pubsubnet3 = stack.pub_sub_list.append(Subnet(stack=stack,
                        route_table=stack.pub_route_table,
                        az=az_c))
    prisubnet1 = stack.pri_sub_list.append(Subnet(stack=stack,
                        route_table=stack.pri_route_table,
                        az=az_a))
    prisubnet2 = stack.pri_sub_list.append(Subnet(stack=stack,
                        route_table=stack.pri_route_table,
                        az=az_b))
    prisubnet3 = stack.pri_sub_list.append(Subnet(stack=stack,
                        route_table=stack.pri_route_table,
                        az=az_c))

    print(stack.to_json(indent=2, separators=(',', ': ')))
if __name__ == "__main__":
    main()
