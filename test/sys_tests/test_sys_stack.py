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
    image_id = 'ami-893f53b3'
    instance_type = 't2.nano'
    stack = Stack(
        title='testStack',
        code_deploy_service_role='instance-iam-role-InstanceProfile-OGL42SZSIQRK',
        keypair='pipeline',
        availability_zones=['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'],
        vpc_cidr='10.0.0.0/16',
        jump_image_id=image_id,
        jump_instance_type=instance_type,
        nat_image_id=image_id,
        nat_instance_type=instance_type,
        units=[{'title': 'app1',
                'protocol': 'HTTP',
                'port': '80',
                'path2ping': 'index.html',
                'minsize': 1,
                'maxsize': 1,
                'image_id': image_id,
                'instance_type': instance_type,
                'userdata': userdata},
               {'title': 'app2',
                'protocol': 'HTTP',
                'port': '80',
                'path2ping': 'index.html',
                'minsize': 1,
                'maxsize': 1,
                'image_id': image_id,
                'instance_type': instance_type,
                'userdata': userdata}],
    )
    print(stack.template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
