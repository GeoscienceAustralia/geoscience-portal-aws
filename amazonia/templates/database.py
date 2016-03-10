# pylint: disable=too-many-arguments, line-too-long

from amazonia.amazonia_resources import *
from amazonia.templates.stack import Stack


class DataBase(Stack):
    def __init__(self):
        """ Class to create a single AZ Database in a vpc """
        super(DataBase, self).__init__()

        my_hiera_client = hiera.HieraClient(hiera_file, hiera_path=hiera_directory, application='my_app_name')
        username = my_hiera_client.get('my_app_name::rds_user')
        password = my_hiera_client.get('my_app_name::rds_password')

        raw_subnets = [self.sub_pri1, self.sub_pri2, self.sub_pri3]

        db_subnet_group = add_db_subnet_group(self, raw_subnets)
        db_security_group = add_security_group(self, self.vpc)
        db = add_db(self, "postgres", db_subnet_group, username, password, db_security_groups=db_security_group)
        add_security_group_ingress(self, db_security_group, "tcp", db.db_port, db.db_port)



