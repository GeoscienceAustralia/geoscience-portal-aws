#!/usr/bin/python3

# import yaml

"""
User values to be used for YAML ingestion and overwrite GA yaml_defaults
"""


userdata = """
#cloud-config
repo_update: true

packages:
 - httpd

runcmd:
 - service httpd start
"""

image_id = 'ami-893f53b3'
instance_type = 't2.nano'
stack_title = 'testStack',
code_deploy_service_role = 'instance-iam-role-InstanceProfile-OGL42SZSIQRK',
keypair = 'pipeline',
availability_zones = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'],
vpc_cidr = '10.0.0.0/16',
jump_image_id = image_id,
jump_instance_type = instance_type,
nat_image_id = image_id,
nat_instance_type = instance_type,
home_cidr = [('GA1', '124.47.132.132/32'), ('GA2', '192.104.44.0/22')],
unit_title ='app1',
protocol = 'HTTP',
port = '80',
path2ping = 'index.html',
minsize = 1,
maxsize = 1

