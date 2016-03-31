#!/usr/bin/python3

from amazonia.classes.elb import Elb
from troposphere import ec2, Ref, Tags, Template


def main():

    vpc = ec2.VPC('MyVPC',
                  CidrBlock='10.0.0.0/16')


if __name__ == "__main__":
    main()
