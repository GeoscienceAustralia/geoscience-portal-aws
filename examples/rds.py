#!/usr/bin/env python

# pylint: disable=missing-docstring, invalid-name, line-too-long, redefined-outer-name, too-many-arguments

from amazonia.cftemplates import Env
from amazonia.amazonia_resources import *
from troposphere import DBInstance, DBSubnetGroup

def main():
    template = Env()
    print(template.to_json(indent=2, separators=(',', ': ')))
# create db subnets

# create db subnet group

# create db security group

# create db instance

# dbname = ""
dballocatedstorage = ""
dbclass = ""
dbengine = ""
dbversion = ""
dbuser = ""
dbpassword = ""
dbmultiaz = ""
dbsubnetgroup = ""
dbsubnets = []
dbsecuritygroups = []


def rds_db(self, dballocatedstorage, dbclass, dbengine, dbversion, dbuser, dbpassword, dbmultiaz, dbsubnets, dbsecuritygroups):
    """Add the RDS instance to template.
    Assumes that template has a VpcId parameter.
    """
    global num_rds
    num_rds += 1

    global num_rds_subnet_group
    num_rds += 1

    non_alphanumeric_title = "RDS" + str(num_rds)
    dbname = trimTitle(non_alphanumeric_title)

    dbsubnetgroup = rds_subnet_group(dbsubnets)

    self.db = self.template.add_resource(DBInstance(
        "DB",
        DBName=dbname,
        AllocatedStorage=dballocatedstorage,
        DBInstanceClass=dbclass,
        Engine=dbengine,
        EngineVersion=dbversion,
        MasterUsername=dbuser,
        MasterUserPassword=dbpassword,
        MultiAZ=dbmultiaz,
        DBSubnetGroupName=isCfObject(dbsubnetgroup),
        VPCSecurityGroups=[dbsecuritygroups]
        ))

def rds_subnet_group(dbsubnets):
    global num_rds_subnet_group
    num_rds += 1

    non_alphanumeric_title = "RDSSubnetGroup" + str(num_rds)
    rds_subnet_group_name = trimTitle(non_alphanumeric_title)

    dbsubnetgroups = self.template.add_resource(
        DBSubnetGroup(rds_subnet_group_name,
                      DBSubnetGroupDescription="Subnets available for the RDS instance.",
                      SubnetIds=dbsubnets
                      ))

    return dbsubnetgroups
if __name__ == "__main__":
    main()
