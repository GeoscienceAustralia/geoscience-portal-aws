
from amazonia.classes.single_instance import SingleInstance
from troposphere import ec2, Ref, Template


def main():

    vpc = ec2.VPC('MyVPC',
                  CidrBlock='10.0.0.0/16')
    subnet = ec2.Subnet('MySubnet',
                        AvailabilityZone='ap-southeast-2a',
                        VpcId=Ref(vpc),
                        CidrBlock='10.0.1.0/24')
    template = Template()
    si = SingleInstance(title='jump',
                              keypair='pipeline',
                              si_image_id='ami-893f53b3',
                              si_instance_type='t2.nano',
                              vpc=vpc,
                              subnet=subnet,
                              stack=template)

    si.stack.add_resource(vpc)
    si.stack.add_resource(subnet)
    print(si.stack.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()