#!/usr/bin/python3

from amazonia.classes.stack import Stack


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
    availability_zones = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']
    keypair = 'pipeline'
    image_id = 'ami-893f53b3',
    instance_type = 't2.nano',
    stack = Stack(
        availability_zones=availability_zones,
        keypair=keypair,
        image_id=image_id,
        instance_type=instance_type,
        userdata=userdata
    )
    print(stack.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
