#!/usr/bin/python3

from amazonia.classes.stack import Stack


def main():
    userdata1 = """#cloud-config
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
    userdata2 = """#cloud-config
repo_update: true

packages:
 - httpd

write_files:
-   content: |
        <html>
        <body background="https://i.ytimg.com/vi/UJ8ZUubtkJo/maxresdefault.jpg">
        </body>
        </html>
    path: /var/www/html/index.html
    permissions: '0644'
    owner: root:root
runcmd:
 - service httpd start
"""

    nat_image_id = 'ami-162c0c75'
    jump_image_id = 'ami-05446966'
    app_image_id = 'ami-05446966'
    instance_type = 't2.micro'
    stack = Stack(
        stack_title='test',
        code_deploy_service_role='arn:aws:iam::658691668407:role/CodeDeployServiceRole',
        keypair='pipeline',
        availability_zones=['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'],
        vpc_cidr='10.0.0.0/16',
        public_cidr='0.0.0.0/0',
        jump_image_id=jump_image_id,
        jump_instance_type=instance_type,
        nat_image_id=nat_image_id,
        nat_instance_type=instance_type,
        home_cidrs=[('GA', '192.104.44.129/32')],
        units=[{'unit_title': 'app1',
                'protocols': ['HTTP'],
                'instanceports': ['80'],
                'loadbalancerports': ['80'],
                'path2ping': '/index.html',
                'minsize': 1,
                'maxsize': 1,
                'health_check_grace_period': 300,
                'health_check_type': 'ELB',
                'image_id': app_image_id,
                'instance_type': instance_type,
                'userdata': userdata1,
                'iam_instance_profile_arn': None,
                'sns_topic_arn': None,
                'sns_notification_types': None,
                'hosted_zone_name': 'gadevs.ga.'},
               {'unit_title': 'app2',
                'protocols': ['HTTP'],
                'instanceports': ['80'],
                'loadbalancerports': ['80'],
                'path2ping': '/index.html',
                'minsize': 1,
                'maxsize': 1,
                'health_check_grace_period': 300,
                'health_check_type': 'ELB',
                'image_id': app_image_id,
                'instance_type': instance_type,
                'userdata': userdata2,
                'iam_instance_profile_arn': None,
                'sns_topic_arn': None,
                'sns_notification_types': None,
                'hosted_zone_name': 'gadevs.ga.'}
               ]

    )
    print(stack.template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
