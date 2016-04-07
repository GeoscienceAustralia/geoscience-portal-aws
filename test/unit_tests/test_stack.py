from nose.tools import *

from amazonia.classes.stack import Stack

userdata = keypair = image_id = instance_type = code_deploy_service_role = vpc_cidr = \
    port = protocol = desiredsize = path2ping = None
availability_zones = []


def setup_resources():
    global userdata, availability_zones, keypair, image_id, instance_type, code_deploy_service_role, vpc_cidr, \
        port, protocol, desiredsize, path2ping, home_cidr
    userdata = """
    #cloud-config
    repo_update: true
    repo_upgrade: all

    packages:
     - httpd

    runcmd:
     - service httpd start
        """
    availability_zones = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']
    keypair = 'pipeline'
    image_id = 'ami-162c0c75'
    instance_type = 't2.nano'
    code_deploy_service_role = 'instance-iam-role-InstanceProfile-OGL42SZSIQRK'
    vpc_cidr = '10.0.0.0/16'
    home_cidr = [('GA1', '124.47.132.132/32'), ('GA2', '192.104.44.0/22')]
    port = '80'
    protocol = 'HTTP'
    desiredsize = 1
    path2ping = 'index.html'


@with_setup(setup_resources())
def test_stack():
    title = 'app'
    stack = create_stack(stack_title=title)
    assert_equals(stack.title, title)

    for num in range(len(availability_zones)):
        # For public subnets
        public_subnet = stack.public_subnets[num]
        assert_equals(public_subnet.CidrBlock, ''.join(['10.0.', str(num), '.0/24']))

        # For private subnets
        private_subnet = stack.private_subnets[num]
        assert_equals(private_subnet.CidrBlock, ''.join(['10.0.', str(num + 100), '.0/24']))


def create_stack(stack_title):
    global userdata, availability_zones, keypair, image_id, instance_type, code_deploy_service_role, vpc_cidr, port, \
        protocol, desiredsize, path2ping, home_cidr
    stack = Stack(
        stack_title=stack_title,
        code_deploy_service_role=code_deploy_service_role,
        keypair=keypair,
        availability_zones=availability_zones,
        vpc_cidr=vpc_cidr,
        home_cidr=home_cidr,
        jump_image_id=image_id,
        jump_instance_type=instance_type,
        nat_image_id=image_id,
        nat_instance_type=instance_type,
        units=[{'unit_title': 'app1',
                'protocol': protocol,
                'port': port,
                'path2ping': path2ping,
                'minsize': desiredsize,
                'maxsize': desiredsize,
                'image_id': image_id,
                'instance_type': instance_type,
                'userdata': userdata},
               {'unit_title': 'app2',
                'protocol': protocol,
                'port': port,
                'path2ping': path2ping,
                'minsize': desiredsize,
                'maxsize': desiredsize,
                'image_id': image_id,
                'instance_type': instance_type,
                'userdata': userdata}],
    )
    return stack
