#!/usr/bin/python3

from troposphere import Ref, Template, ec2

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.subnet import Subnet
from amazonia.classes.unit import Unit


class Stack(object):
    def __init__(self, **kwargs):
        """
        Create a vpc, nat, jumphost, internet gateway, public/private route tables, public/private subnets
         and collection of Amazonia units
        AWS CloudFormation -
         http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param code_deploy_service_role: ARN to code deploy IAM role
        :param keypair: ssh keypair to be used throughout stack
        :param availability_zones: availability zones to use
        :param vpc_cidr: cidr pattern for vpc
        :param jump_image_id: AMI for jumphost
        :param jump_instance_type: instance type for jumphost
        :param nat_image_id: AMI for nat
        :param nat_instance_type: instance type for nat
        :param units: list of unit dicts (title, protocol, port, path2ping, minsize, maxsize, image_id,
         instance_type, userdata)
        """
        super(Stack, self).__init__()
        self.title = kwargs['title']
        self.template = Template()
        self.code_deploy_service_role = kwargs['code_deploy_service_role']
        self.keypair = kwargs['keypair']
        self.availability_zones = kwargs['availability_zones']
        self.vpc_cidr = kwargs['vpc_cidr']

        self.units = []
        self.private_subnets = []
        self.public_subnets = []

        self.vpc = self.template.add_resource(ec2.VPC(self.title + 'Vpc', CidrBlock=self.vpc_cidr))
        self.internet_gateway = self.template.add_resource(ec2.InternetGateway(self.title + 'Ig'))
        self.gateway_attachment = self.template.add_resource(
            ec2.VPCGatewayAttachment(self.internet_gateway.title + 'Atch',
                                     VpcId=Ref(self.vpc),
                                     InternetGatewayId=Ref(self.internet_gateway)))
        self.public_route_table = self.template.add_resource(ec2.RouteTable(self.title + 'PubRt',
                                                                            VpcId=Ref(self.vpc)))
        self.private_route_table = self.template.add_resource(ec2.RouteTable(self.title + 'PriRt',
                                                                             VpcId=Ref(self.vpc)))
        for az in self.availability_zones:
            self.private_subnets.append(Subnet(template=self.template,
                                               stack_title=self.title,
                                               route_table=self.private_route_table,
                                               az=az,
                                               vpc=self.vpc,
                                               is_public=False,
                                               cidr=self.generate_subnet_cidr(is_public=False)).subnet)
            self.public_subnets.append(Subnet(template=self.template,
                                              stack_title=self.title,
                                              route_table=self.public_route_table,
                                              az=az,
                                              vpc=self.vpc,
                                              is_public=True,
                                              cidr=self.generate_subnet_cidr(is_public=True)
                                              ).subnet)

        self.jump = SingleInstance(
            title=self.title + 'Jump',
            keypair=self.keypair,
            si_image_id=kwargs['jump_image_id'],
            si_instance_type=kwargs['jump_instance_type'],
            subnet=self.public_subnets[0],
            vpc=self.vpc,
            template=self.template
        )

        self.nat = SingleInstance(
            title=self.title + 'Nat',
            keypair=self.keypair,
            si_image_id=kwargs['nat_image_id'],
            si_instance_type=kwargs['nat_instance_type'],
            subnet=self.public_subnets[0],
            vpc=self.vpc,
            template=self.template
        )

        for unit in kwargs['units']:
            self.units.append(Unit(title=self.title + unit['title'],
                                   vpc=self.vpc,
                                   template=self.template,
                                   protocol=unit['protocol'],
                                   port=unit['port'],
                                   path2ping=unit['path2ping'],
                                   public_subnets=self.public_subnets,
                                   private_subnets=self.private_subnets,
                                   minsize=unit['minsize'],
                                   maxsize=unit['maxsize'],
                                   keypair=self.keypair,
                                   image_id=unit['image_id'],
                                   instance_type=unit['instance_type'],
                                   userdata=unit['userdata'],
                                   service_role_arn=self.code_deploy_service_role,
                                   nat=self.nat,
                                   jump=self.jump,
                                   ))

    def generate_subnet_cidr(self, is_public):
        """
        Function to help create Class C subnet CIDRs from Class A VPC CIDRs
        :param is_public: boolean for public or private subnet determined by route table
        :return: Subnet CIDR based on Public or Private and previous subnets created e.g. 10.1.2.0/24 or 10.0.1.0/24
        """
        # 3rd Octect: Obtain length of pub or pri subnet list
        octect_3 = len(self.public_subnets) if is_public else len(self.private_subnets) + 100
        cidr_split = self.vpc.CidrBlock.split('.')  # separate VPC CIDR for renaming
        cidr_split[2] = str(octect_3)  # set 3rd octect based on public or private
        cidr_last = cidr_split[3].split('/')  # split last group to change subnet mask
        cidr_last[1] = '24'  # set subnet mask
        cidr_split[3] = '/'.join(cidr_last)  # join last group for subnet mask

        return '.'.join(cidr_split)
