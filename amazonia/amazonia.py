#!/usr/bin/python3
"""
Ingest User YAML and GA defaults YAML
Overwrite GA defaults YAML with User YAML

"""
import yaml
# from amazonia.amazonia.classes.stack import Stack


def read_yaml(user_yaml):
    """ Ingest user YAML
    """
    with open(user_yaml, 'r') as stack_yaml:
        return yaml.load(stack_yaml)
        # print('stack_data={0}'.format(stack_data))


def read_defaults(default_yaml):
    """ Ingest  GA default YAML
    """
    with open(default_yaml, 'r') as default_yaml:
        return yaml.load(default_yaml)


def set_values(stack_data, default_data):
    """ Assign values
    """
    united_data = dict()
    stack_value_list = ['stack_title',
                        'code_deploy_service_role',
                        'keypair',
                        'availability_zones',
                        'vpc_cidr',
                        'jump_image_id',
                        'jump_instance_type',
                        'nat_image_id',
                        'nat_instance_type',
                        'home_cidr',
                        'units']

    for value in stack_value_list:
        united_data[value] = get_values(value)

    unit_value_list = ['unit_title',
                       'protocol',
                       'port']

    for unit_title, unit_values in stack_data['units'].items():
        united_data['units'][unit_title] = unit_title
        for unit_value in unit_value_list:
            united_data['units'][unit_title][unit_value] = get_values(unit_values)

    print(united_data)


    # TODO YAML some DICTS

    # for unit_title, unit_values in units.items():
    #
    #     unit_title = unit_title
    #     # validate_title(united_data['unit_title'])
    #     print(unit_title)
    #     protocol = unit_values.get('protocol', default_data['protocol'])
    #     print(protocol)
    #     port = unit_values.get('port', default_data['port'])
    #     print(port)

    # unit_num = 1
    # for unit in units:
    #     unit_title = units.get('unit', 'unit' + str(unit_num))
    #     unit_num += 1
    #     print(unit_title)

    """ Validate Data
    """
    # validate_title(united_data['stack_title'])
    # validate_cidr(united_data['vpc_cidr'])

    return united_data


def get_values(value):
    united_value = stack_data.get(value, default_data[value])
    return united_value


def create_stack(united_data):
    """
    Create Stack using amazonia
    :param united_data: Dictionary of yaml consisting of user yaml values with default yaml values for any missing keys
    return: Troposphere template object
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

# def validate_title(stack_or_unit_title):
    # TODO stack_title must be alphanumeric

# def validate_cidr(cidr):
    # TODO cidr[0] must must cidr notation
    # TODO cidr[1] must be alphanumeric

# def unencrypted_access_keys():
    # TODO regex for enecrypted


def __main__():
    """
    :param yaml: User yaml document used to read stack values
    :param defaults: Company yaml to read in company default values
    :return: Cloud Formation template
    """
    stack_data = read_yaml('./amazonia/amazonia.yaml')
    default_data = read_defaults('./amazonia/classes/amazonia_ga_defaults.yaml')
    united_data = set_values(stack_data, default_data)

    """ Print Cloud Formation Template
    """
    # print(stack.template.to_json(indent=2, separators=(',', ': ')))