#!/usr/bin/python3

from nose.tools import *
from troposphere import ec2, Ref, Tags, Template

from amazonia.classes.database import Database


def test_database():
    template = Template()
    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))
    internet_gateway = template.add_resource(ec2.InternetGateway('MyInternetGateway',
                                                                 Tags=Tags(Name='MyInternetGateway')))

    gateway_attachment = template.add_resource(ec2.VPCGatewayAttachment('MyVPCGatewayAttachment',
                                                                        InternetGatewayId=Ref(internet_gateway),
                                                                        VpcId=Ref(vpc)))
    gateway_attachment.DependsOn = internet_gateway.title

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
    db = Database(title='MyDb',
                  subnets=public_subnets,
                  vpc=vpc,
                  template=template,
                  db_instance_type='db.m1.small',
                  db_engine='postgres',
                  db_port='5432'
                  )
    assert_equals(db.trop_db.DBInstanceClass, 'db.m1.small')
    assert_equals(db.trop_db.Engine, 'postgres')
    assert_equals(db.trop_db.Port, '5432')