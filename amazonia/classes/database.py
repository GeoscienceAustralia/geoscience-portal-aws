#!/usr/bin/python3

from amazonia.classes.security_enabled_object import SecurityEnabledObject
from troposphere import Tags, Ref, rds, Join, Output, GetAtt, Parameter


class Database(SecurityEnabledObject):
    def __init__(self, title, vpc, template, subnets, db_instance_type, db_engine, db_port):
        """ Class to create an RDS and DB subnet group in a vpc
        :param title: Title of the autoscaling application e.g 'webApp1', 'api2' or 'dataprocessing'
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param template: Troposphere stack to append resources to
        :param subnets: subnets to create autoscaled instances in
        :param db_instance_type: Size of the RDS instance
        :param db_engine: DB engine type (Postgres, Oracle, MySQL, etc)
        :param db_port: Port of RDS instance
        """
        self.title = title + 'Rds'
        self.db_subnet_group_title = title + "Dsg"
        super(Database, self).__init__(vpc=vpc, title=self.title, template=template)

        self.db_subnet_group = template.add_resource(
            rds.DBSubnetGroup(self.db_subnet_group_title,
                              DBSubnetGroupDescription=self.db_subnet_group_title,
                              SubnetIds=[Ref(x) for x in subnets],
                              Tags=Tags(Name=self.db_subnet_group_title)))

        self.username = self.template.add_parameter(Parameter(
            self.title+'Username', Type='String', Description='Master username of {0} RDS'.format(self.title),
            NoEcho=True))

        self.password = self.template.add_parameter(Parameter(
            self.title+'Password', Type='String', Description='Master password of {0} RDS'.format(self.title),
            NoEcho=True))

        self.db = template.add_resource(
            rds.DBInstance(self.title,
                           AllocatedStorage=5,
                           AllowMajorVersionUpgrade=True,
                           AutoMinorVersionUpgrade=True,
                           MultiAZ=True,
                           DBInstanceClass=db_instance_type,
                           DBSubnetGroupName=Ref(self.db_subnet_group),
                           Engine=db_engine,
                           MasterUsername=Ref(self.username),
                           MasterUserPassword=Ref(self.password),
                           Port=db_port,
                           VPCSecurityGroups=[Ref(self.security_group)],
                           Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', self.title]))))

        self.template.add_output(Output(
            self.db.title+'Address',
            Description='Address of the {0} RDS'.format(self.title),
            Value=GetAtt(self.db, 'Endpoint.Address')))

        self.template.add_output(Output(
            self.db.title+'Port',
            Description='Port of the {0} RDS'.format(self.title),
            Value=GetAtt(self.db, 'Endpoint.Port')))
