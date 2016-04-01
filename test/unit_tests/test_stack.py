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
