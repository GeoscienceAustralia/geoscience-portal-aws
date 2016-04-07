#!/usr/bin/python3

from amazonia.classes.stack import Stack


def main():
    userdata = """#cloud-config
repo_update: true

packages:
 - httpd

write_files:
-   content: |
        <html>
        <body background="http://mulataria.com/wp-content/uploads/2015/05/269944_Papel-de-Parede-Vitoria-regia-na-Amazonia_1920x1200.jpg">
        </body>
        </html>
    path: /var/www/html/index.html
    permissions: '0644'
    owner: root:root
runcmd:
 - service httpd start
"""

    nat_image_id = 'ami-162c0c75'
    jump_image_id = 'ami-162c0c75'
    app_image_id = 'ami-f2210191'
    instance_type = 't2.nano'
    stack = Stack(
        stack_title='testStack',
        code_deploy_service_role='instance-iam-role-InstanceProfile-OGL42SZSIQRK',
        keypair='pipeline',
        availability_zones=['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'],
        vpc_cidr='10.0.0.0/16',
        jump_image_id=jump_image_id,
        jump_instance_type=instance_type,
        nat_image_id=nat_image_id,
        nat_instance_type=instance_type,
        home_cidr=[('GA', '192.104.44.129/32')],
        units=[{'unit_title': 'app1',
                'protocol': 'HTTP',
                'port': '80',
                'path2ping': '/index.html',
                'minsize': 1,
                'maxsize': 1,
                'image_id': app_image_id,
                'instance_type': instance_type,
                'userdata': userdata}]

    )
    print(stack.template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
