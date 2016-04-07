#!/usr/bin/python3
"""
Ingest User YAML and GA defaults YAML
Overwrite GA defaults YAML with User YAML

"""
import yaml
# from amazonia.amazonia.classes.stack import Stack


""" Ingest user YAML files and GA default YAML
"""

# TODO Parse in amazonia.yaml as arguement
with open('./amazonia/amazonia.yaml', 'r') as stack_yaml:
    stack_data = (yaml.load(stack_yaml))
    # print('stack_data={0}'.format(stack_data))

with open('./amazonia/classes/amazonia_ga_defaults.yaml', 'r') as default_yaml:
    default_data = (yaml.load(default_yaml))


""" Assign values
"""

# stack_title = stack_data.get('stack_title', default_data['stack_title'])
# code_deploy_service_role = stack_data.get('code_deploy_service_role', default_data['code_deploy_service_role'])
# keypair = stack_data.get('keypair', default_data['keypair'])
# availability_zones = stack_data.get('availability_zones', default_data['availability_zones'])
# vpc_cidr = stack_data.get('vpc_cidr', default_data['vpc_cidr'])
# jump_image_id = stack_data.get('jump_image_id', default_data['jump_image_id'])
# jump_instance_type = stack_data.get('jump_instance_type', default_data['jump_instance_type'])
# nat_image_id = stack_data.get('nat_image_id', default_data['nat_image_id'])
# nat_instance_type = stack_data.get('nat_instance_type', default_data['nat_instance_type'])
# home_cidr = stack_data.get('home_cidr', default_data['home_cidr'])
units = stack_data['units']
# print(units)

for unit_title, unit_values in units.items():
    unit_title = unit_title
    print(unit_title)
    protocol = unit_values.get('protocol', default_data['protocol'])
    print(protocol)
    port = unit_values.get('port', default_data['port'])
    print(port)

# unit_num = 1
# for unit in units:
#     unit_title = units.get('unit', 'unit' + str(unit_num))
#     unit_num += 1
#     print(unit_title)
""" Call Stack
"""

# stack = Stack(
#     stack_title=stack_title,
#     code_deploy_service_role='instance-iam-role-InstanceProfile-OGL42SZSIQRK',
#     keypair='pipeline',
#     availability_zones=['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'],
#     vpc_cidr='10.0.0.0/16',
#     jump_image_id=image_id,
#     jump_instance_type=instance_type,
#     nat_image_id=image_id,
#     nat_instance_type=instance_type,
#     home_cidr=[('GA1', '124.47.132.132/32'), ('GA2', '192.104.44.0/22')],
#     units=[{'unit_title': 'app1',
#             'protocol': 'HTTP',
#             'port': '80',
#             'path2ping': 'index.html',
#             'minsize': 1,
#             'maxsize': 1,
#             'image_id': image_id,
#             'instance_type': instance_type,
#             'userdata': userdata},
#            {'unit_title': 'app2',
#             'protocol': 'HTTP',
#             'port': '80',
#             'path2ping': 'index.html',
#             'minsize': 1,
#             'maxsize': 1,
#             'image_id': image_id,
#             'instance_type': instance_type,
#             'userdata': userdata}],

""" Validate YAML Values
"""

# def validate_stack_title(stack_title):
    # TODO stack_title must be alphanumeric

# def validate_cidr():
    # TODO cidr[0] must must cidr notation
    # TODO cidr[1] must be alphanumeric

# def unencrypted_access_keys():
    # TODO regex for enecrypted

""" Print Cloud Formation Template
"""

# print(stack.template.to_json(indent=2, separators=(',', ': ')))