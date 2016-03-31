#!/usr/bin/python3

from troposphere import ec2, Ref, Template

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.unit import Unit


def main():
    userdata = """
#cloud-config
repo_update: true
repo_upgrade: all

packages:
 - httpd

runcmd:
 - service httpd start
    """
    template = Template()

    vpc = ec2.VPC('MyVPC',
                  CidrBlock='10.0.0.0/16')
    private_subnets = [ec2.Subnet('MySubnet',
                                  AvailabilityZone='ap-southeast-2a',
                                  VpcId=Ref(vpc),
                                  CidrBlock='10.0.1.0/24')]
    public_subnets = [ec2.Subnet('MySubnet2',
                                 AvailabilityZone='ap-southeast-2a',
                                 VpcId=Ref(vpc),
                                 CidrBlock='10.0.2.0/24')]
    nat = SingleInstance(title='nat',
                         keypair='pipeline',
                         si_image_id='ami-893f53b3',
                         si_instance_type='t2.nano',
                         vpc=vpc,
                         subnet=public_subnets[0],
                         stack=template)
    jump = SingleInstance(title='jump',
                          keypair='pipeline',
                          si_image_id='ami-893f53b3',
                          si_instance_type='t2.nano',
                          vpc=vpc,
                          subnet=public_subnets[0],
                          stack=template)
    unit1 = Unit(
        title='app1',
        vpc=vpc,
        stack=template,
        protocol='HTTP',
        port='80',
        path2ping='HTTP:8080/error/noindex.html',
        public_subnets=public_subnets,
        private_subnets=private_subnets,
        minsize=1,
        maxsize=1,
        keypair='pipeline',
        image_id='ami-893f53b3',
        instance_type='t2.nano',
        userdata=userdata,
        service_role_arn='instance-iam-role-InstanceProfile-OGL42SZSIQRK',
        nat=nat,
        jump=jump,
    )

    unit2 = Unit(
        title='app2',
        vpc=vpc,
        stack=template,
        protocol='HTTP',
        port='80',
        path2ping='HTTP:8080/error/noindex.html',
        public_subnets=public_subnets,
        private_subnets=private_subnets,
        minsize=1,
        maxsize=1,
        keypair='pipeline',
        image_id='ami-893f53b3',
        instance_type='t2.nano',
        userdata=userdata,
        service_role_arn='instance-iam-role-InstanceProfile-OGL42SZSIQRK',
        nat=nat,
        jump=jump,
    )

    unit1.add_unit_flow(other=unit2, protocol='HTTP', port='80')
    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
