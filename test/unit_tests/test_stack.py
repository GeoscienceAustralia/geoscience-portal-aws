from nose.tools import *

from amazonia.classes.stack import Stack

userdata = availability_zones = keypair = image_id = instance_type = None


def setup_resources():
    global userdata, availability_zones, keypair, image_id, instance_type
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
    image_id = 'ami-893f53b3',
    instance_type = 't2.nano',


@with_setup(setup_resources())
def test_stack():
    title = 'app'
    stack = create_stack(title=title)


def create_stack(**kwargs):
    global userdata, availability_zones, keypair, image_id, instance_type
    stack = Stack(
        availability_zones=availability_zones,
        keypair=keypair,
        image_id=image_id,
        instance_type=instance_type,
        userdata=userdata
    )
    return stack

@with_setup(setup_resources)
def test_sub_cidr():
    """ Validate that subnet CIDR is correctly created for private/public subnets for number of availablity zones
    """
    for num in range(len(az)):
        # For public subnets
        helper_pub_subnet = Subnet.sub_cidr(stack, 'Public')
        stack.pub_sub_list.append(helper_pub_subnet)
        assert_equals(helper_pub_subnet, ''.join(['10.0.', str(num), '.0/24']))

        # For private subnets
        helper_pri_subnet = Subnet.sub_cidr(stack, 'Private')
        stack.pri_sub_list.append(helper_pri_subnet)
        assert_equals(helper_pri_subnet, ''.join(['10.0.', str(num + 100), '.0/24']))