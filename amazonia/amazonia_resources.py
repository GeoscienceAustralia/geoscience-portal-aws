# pylint: disable=too-many-arguments, line-too-long

"""

The functions in this module generate cloud formation scripts that install common AWS environments and components

"""

from troposphere import Ref, Tags, Join, Base64, GetAtt, ec2, rds, route53
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration, Tag
import troposphere.elasticloadbalancing as elb
import inflection
import hiera
import os
import yaml

try:
    hiera_directory = os.getenv('HIERA_PATH', "/etc/puppet/hieradata/")
    hiera_file = hiera_directory + "hiera.yaml"
    hiera_client = hiera.HieraClient(hiera_file, hiera_path=hiera_directory, application='amazonia')

    NAT_IMAGE_ID = hiera_client.get('amazonia::nat_image_id')
    NAT_INSTANCE_TYPE = hiera_client.get('amazonia::nat_instance_type')
    ENVIRONMENT_NAME = hiera_client.get('amazonia::environment')
    AVAILABILITY_ZONES = [hiera_client.get('amazonia::availability_zone1'), hiera_client.get('amazonia::availability_zone2')]
    REGION = AVAILABILITY_ZONES[0][:-1]
    WEB_IMAGE_ID = hiera_client.get('amazonia::web_image_id') # OLD AMI: "ami-c11856fb"  # BASE AMI: "ami-ba6f4ad9"
    WEB_INSTANCE_TYPE = hiera_client.get('amazonia::web_instance_type')
    ASG_MIN_INSTANCES = int(hiera_client.get('amazonia::asg_min_instances'))

    # CIDRs
    PUBLIC_COMPANY_CIDR = hiera_client.get('amazonia::public_company_cidr')
    VPC_CIDR = hiera_client.get('amazonia::vpc_cidr')
    PUBLIC_SUBNET_AZ1_CIDR = hiera_client.get('amazonia::public_subnet_az1_cidr')
    PUBLIC_SUBNET_AZ2_CIDR = hiera_client.get('amazonia::public_subnet_az2_cidr')
    PRIVATE_SUBNET_AZ1_CIDR = hiera_client.get('amazonia::private_subnet_az1_cidr')
    PRIVATE_SUBNET_AZ2_CIDR = hiera_client.get('amazonia::private_subnet_az2_cidr')
    PUBLIC_CIDR = hiera_client.get('amazonia::public_cidr')
    PUBLIC_SUBNET_NAME = hiera_client.get('amazonia::public_subnet_name')
    PRIVATE_SUBNET_NAME = hiera_client.get('amazonia::private_subnet_name')

    # WEB SERVER BOOTSTRAP SCRIPTS
    WEB_SERVER_AZ1_USER_DATA = hiera_client.get('amazonia::web_server_az1_user_data')
    WEB_SERVER_AZ2_USER_DATA = hiera_client.get('amazonia::web_server_az2_user_data')

    # Bootstrap variables for instances & auto scaling groups
    BOOTSTRAP_S3_DEPLOY_REPO = hiera_client.get('amazonia::bootstrap_s3_deploy_repo')
    BOOTSTRAP_SCRIPT_NAME = hiera_client.get('amazonia::bootstrap_script_name')
except Exception:
    if os.path.isfile('./config.yaml'):
        f=open('config.yaml')
        variables=yaml.load(f)
        NAT_IMAGE_ID = variables['nat_image_id']
        NAT_INSTANCE_TYPE = variables['nat_instance_type']
        ENVIRONMENT_NAME = variables['environment']
        AVAILABILITY_ZONES = [variables['availability_zone1'], variables['availability_zone2']]
        WEB_IMAGE_ID = variables['web_image_id']
        WEB_INSTANCE_TYPE = variables['web_instance_type']
        ASG_MIN_INSTANCES = int(variables['asg_min_instances'])

        # CIDRs
        PUBLIC_COMPANY_CIDR = variables['public_company_cidr']
        VPC_CIDR = variables['vpc_cidr']
        PUBLIC_SUBNET_AZ1_CIDR = variables['public_subnet_az1_cidr']
        PUBLIC_SUBNET_AZ2_CIDR = variables['public_subnet_az2_cidr']
        PRIVATE_SUBNET_AZ1_CIDR = variables['private_subnet_az1_cidr']
        PRIVATE_SUBNET_AZ2_CIDR = variables['private_subnet_az2_cidr']
        PUBLIC_CIDR = variables['public_cidr']
        PUBLIC_SUBNET_NAME = variables['public_subnet_name']
        PRIVATE_SUBNET_NAME = variables['private_subnet_name']

        # WEB SERVER BOOTSTRAP SCRIPTS
        WEB_SERVER_AZ1_USER_DATA = variables['web_server_az1_user_data']
        WEB_SERVER_AZ2_USER_DATA = variables['web_server_az2_user_data']

        # Bootstrap variables for instances & auto scaling groups
        BOOTSTRAP_S3_DEPLOY_REPO = variables['bootstrap_s3_deploy_repo']
        BOOTSTRAP_SCRIPT_NAME = variables['bootstrap_script_name']
    else:
        print("ERROR: Hiera, or config.yaml could not be found.")
        print("       Amazonia expects either a HIERA_PATH environment")
        print("       variable pointing to the location of a hiera config")
        print("       or a config.yaml to be in the root of the amazonia directory")
        print("       See README.md for more information.")
        exit(1) # Exit with error code 1


# Handler for switching Availability Zones
current_az = 0

# numbers to count objects created
num_vpcs = 0
num_subnets = 0
num_route_tables = 0
num_internet_gateways = 0
num_routes = 0
num_nats = 0
num_security_groups = 0
num_ingress_rules = 0
num_egress_rules = 0
num_load_balancers = 0
num_launch_configs = 0
num_web_instances = 0
num_web_security_groups = 0
num_route_table_associations = 0
num_auto_scaling_groups = 0
num_db = 0
num_db_subnet_group = 0
num_db_instance = 0
num_r53_hosted_zone = 0
num_r53_record_set = 0

def isCfObject(object):
    if type(object) is str:
        returnObject = object
    else:
        returnObject = Ref(object)

    return returnObject


def switch_availability_zone():
    """
        A simple function to switch Availability zones.
    """
    global current_az
    if current_az == 0:
        current_az = 1
    else:
        current_az = 0


def add_vpc(template, cidr):
    """
        Creates a VPC resource and adds it to the given template object.
    """

    global num_vpcs
    num_vpcs += 1

    non_alphanumeric_title = "VPC" + str(num_vpcs)
    vpc_title = trimTitle(non_alphanumeric_title)

    vpc = template.add_resource(ec2.VPC(vpc_title,
                                        CidrBlock=cidr,
                                        Tags=Tags(Name=name_tag(vpc_title),
                                                  Environment=ENVIRONMENT_NAME)))
    return vpc


def add_subnet(template, vpc, name, cidr):
    global num_subnets
    num_subnets += 1

    non_alphanumeric_title = name + str(num_subnets)
    subnet_title = trimTitle(non_alphanumeric_title)

    subnet = template.add_resource(ec2.Subnet(subnet_title,
                                                     AvailabilityZone=AVAILABILITY_ZONES[current_az],
                                                     VpcId=isCfObject(vpc),
                                                     CidrBlock=cidr,
                                                     Tags=Tags(Name=name_tag(subnet_title),
                                                               Environment=ENVIRONMENT_NAME)))
    return subnet


def add_route_table(template, vpc, route_type=""):
    global num_route_tables
    num_route_tables = num_route_tables + 1

    non_alphanumeric_title = route_type + "RouteTable" + str(num_route_tables)
    route_table_title = trimTitle(non_alphanumeric_title)

    route_table = template.add_resource(ec2.RouteTable(route_table_title,
                                                       VpcId=isCfObject(vpc),
                                                       Tags=Tags(Name=name_tag(route_table_title)),
                                                      ))
    return route_table


def add_route_table_subnet_association(template, route_table, subnet):
    global num_route_table_associations
    num_route_table_associations += 1

    if type(route_table) is str:
        route_table_name = route_table
    else:
        route_table_name = route_table.title

    # Associate the route table with the subnet
    route_table_association = template.add_resource(ec2.SubnetRouteTableAssociation(
        route_table_name + "Association" + str(num_route_table_associations),
        SubnetId=isCfObject(subnet),
        RouteTableId=isCfObject(route_table),
    ))

    return route_table_association


def add_internet_gateway(template):
    global num_internet_gateways
    num_internet_gateways = num_internet_gateways + 1

    non_alphanumeric_title = "InternetGateway" + str(num_internet_gateways)
    internet_gateway_title = trimTitle(non_alphanumeric_title)

    internet_gateway = template.add_resource(ec2.InternetGateway(internet_gateway_title,
                                                                 Tags=Tags(Name=name_tag(internet_gateway_title),
                                                                           Environment=ENVIRONMENT_NAME)
                                                                ))
    return internet_gateway


def add_internet_gateway_attachment(template, vpc, internet_gateway):

    if type(internet_gateway) is str:
        internet_gateway_name = internet_gateway
    else:
        internet_gateway_name = internet_gateway.title

    attachment_title = internet_gateway_name + "Attachment"
    gateway_attachment = template.add_resource(ec2.VPCGatewayAttachment(attachment_title,
                                                                        VpcId=isCfObject(vpc),
                                                                        InternetGatewayId=isCfObject(internet_gateway),
                                                                       ))

    return gateway_attachment


def add_route_ingress_via_gateway(template, route_table, internet_gateway, cidr, dependson = ""):
    global num_routes
    num_routes += 1
    route = template.add_resource(ec2.Route(
        "InboundRoute" + str(num_routes),
        GatewayId=isCfObject(internet_gateway),
        RouteTableId=isCfObject(route_table),
        DestinationCidrBlock=cidr
    ))

    if not dependson == "":
        route.DependsOn = [isCfObject(x) for x in dependson]

    return route


def add_route_egress_via_NAT(template, route_table, nat, dependson=""):
    global num_routes
    num_routes += 1

    route = template.add_resource(ec2.Route("OutboundRoute" + str(num_routes),
                                    InstanceId=isCfObject(nat),
                                    RouteTableId=isCfObject(route_table),
                                    DestinationCidrBlock=PUBLIC_CIDR,
                                   ))

    if not dependson == "":
        route.DependsOn = [isCfObject(x) for x in dependson]

    return route


def add_security_group(template, vpc):
    global num_security_groups
    num_security_groups += 1

    non_alphanumeric_title = "SecurityGroup" + str(num_security_groups)
    sg_title = trimTitle(non_alphanumeric_title)

    sg = template.add_resource(ec2.SecurityGroup(sg_title,
                                                 GroupDescription="Security group",
                                                 VpcId=isCfObject(vpc),
                                                 Tags=Tags(Name=name_tag(sg_title))))

    return sg


def add_security_group_ingress(template, security_group, protocol, from_port, to_port, cidr="", source_security_group=""):
    """
        Add a rule to security group that allows incoming traffic to any resources (e.g. EC2 instances)
            assigned to the security group.

        security_group: the security group to add the rule to
        protocol: the protocol to allow eg. tcp
        from_port: the origin port
        to_port: the destination port (this allows port conversion)
        cidr: the cidr range that is allowed to send traffic
        source_security_group: to receive traffic from other resources allocated to source_security_group
    """

    global num_ingress_rules
    num_ingress_rules += 1
    if type(security_group) is str:
        security_group_name = security_group
    else:
        security_group_name = security_group.title
    if not protocol == "-1":
        non_alphanumeric_title = security_group_name + 'Ingress' + protocol + str(num_ingress_rules)
    else:
        non_alphanumeric_title = security_group_name + 'IngressAll' + str(num_ingress_rules)

    ingress_title = trimTitle(non_alphanumeric_title)

    sg_ingress = template.add_resource(ec2.SecurityGroupIngress(ingress_title,
                                                                IpProtocol=protocol,
                                                                FromPort=from_port,
                                                                ToPort=to_port,
                                                                GroupId=isCfObject(security_group)
                                                               ))
    if not source_security_group == "":
        sg_ingress.SourceSecurityGroupId = GetAtt(source_security_group.title, "GroupId")
    else:
        if not cidr == "":
            sg_ingress.CidrIp = cidr
    return sg_ingress


def add_security_group_egress(template, security_group, protocol, from_port, to_port, cidr="", destination_security_group=""):

    global num_egress_rules
    num_egress_rules += 1
    if type(security_group) is str:
        security_group_name = security_group
    else:
        security_group_name = security_group.title
    if not protocol == "-1":
        non_alphanumeric_title = security_group_name + 'Egress' + protocol + str(num_egress_rules)
    else:
        non_alphanumeric_title = security_group_name + 'EgressAll' + str(num_egress_rules)

    egress_title = trimTitle(non_alphanumeric_title)

    sg_egress = template.add_resource(ec2.SecurityGroupEgress(egress_title,
                                                              IpProtocol=protocol,
                                                              FromPort=from_port,
                                                              ToPort=to_port,
                                                              GroupId=isCfObject(security_group)
                                                             ))

    if not destination_security_group == "":
        if type(destination_security_group) == str:
            sg_egress.DestinationSecurityGroupId = destination_security_group
        else:
            sg_egress.DestinationSecurityGroupId = GetAtt(destination_security_group, "GroupId")
    else:
        if not cidr == "":
            sg_egress.CidrIp = cidr

    return sg_egress


def add_nat(template, subnet, key_pair_name, security_group):
    global num_nats
    num_nats += 1

    non_aplhanumeric_title = "NAT" + str(num_nats)
    nat_title = trimTitle(non_aplhanumeric_title)

    nat = template.add_resource(ec2.Instance(
        nat_title,
        KeyName=key_pair_name,
        ImageId=NAT_IMAGE_ID,
        InstanceType=NAT_INSTANCE_TYPE,
        NetworkInterfaces=[ec2.NetworkInterfaceProperty(
            GroupSet=[isCfObject(security_group)],
            AssociatePublicIpAddress=True,
            DeviceIndex="0",
            DeleteOnTermination=True,
            SubnetId=isCfObject(subnet),
        )],
        SourceDestCheck=False,
        Tags=Tags(
            Name=name_tag(nat_title),
        ),
    ))
    return nat


def add_web_instance(template, key_pair_name, subnet, security_group, userdata, public=True, app_name="default"):
    global num_web_instances
    num_web_instances += 1

    non_alphanumeric_title = "WebServer" + str(num_web_instances)
    instance_title = trimTitle(non_alphanumeric_title)

    instance = template.add_resource(ec2.Instance(
        instance_title,
        InstanceType=WEB_INSTANCE_TYPE,
        KeyName=key_pair_name,
        SourceDestCheck=False,
        ImageId=WEB_IMAGE_ID,
        NetworkInterfaces=[ec2.NetworkInterfaceProperty(
            GroupSet=[isCfObject(security_group)],
            AssociatePublicIpAddress=public,
            DeviceIndex="0",
            DeleteOnTermination=True,
            SubnetId=isCfObject(subnet),
        )],
        Tags=Tags(
            Name=name_tag(instance_title),
            S3_DEPLOY_REPO=BOOTSTRAP_S3_DEPLOY_REPO,
            S3_DEPLOY_REPO_PATH=app_name,
            SCRIPT_NAME=BOOTSTRAP_SCRIPT_NAME
        ),
        UserData=Base64(userdata),
    ))
    return instance


def add_load_balancer(template, subnets, healthcheck_target, security_groups, loadbalancerport="80", protocol="HTTP",
                      instanceport="80", instanceprotocol="HTTP", resources="", dependson=""):
    global num_load_balancers
    num_load_balancers += 1

    non_alphanumeric_title = "ElasticLoadBalancer" + str(num_load_balancers)
    elb_title = trimTitle(non_alphanumeric_title)

    return_elb = template.add_resource(elb.LoadBalancer(elb_title,
                                                        CrossZone=True,
                                                        HealthCheck=elb.HealthCheck(Target=healthcheck_target,
                                                                                    HealthyThreshold="2",
                                                                                    UnhealthyThreshold="5",
                                                                                    Interval="15",
                                                                                    Timeout="5"),
                                                        Listeners=[elb.Listener(LoadBalancerPort=loadbalancerport,
                                                                                Protocol=protocol,
                                                                                InstancePort=instanceport,
                                                                                InstanceProtocol=instanceprotocol)],
                                                        Scheme="internet-facing",
                                                        SecurityGroups=[isCfObject(x) for x in security_groups],
                                                        Subnets=[isCfObject(x) for x in subnets],
                                                        Tags=Tags(Name=name_tag(elb_title))))

    if not resources == "":
        return_elb.Instances = [isCfObject(x) for x in resources]

    if not dependson == "":
        return_elb.DependsOn = [isCfObject(x) for x in dependson]

    return return_elb


def add_auto_scaling_group(template, max_instances, subnets, instance="", launch_configuration="", health_check_type="", dependson="", load_balancer="", multiAZ=False, app_name="default"):
    global num_auto_scaling_groups
    num_auto_scaling_groups += 1

    non_alphanumeric_title = str(app_name) + str(ENVIRONMENT_NAME) + "AutoScalingGroup" + str(num_auto_scaling_groups)
    auto_scaling_group_title = trimTitle(non_alphanumeric_title)

    asg = template.add_resource(AutoScalingGroup(
        auto_scaling_group_title,
        MinSize=ASG_MIN_INSTANCES,
        MaxSize=max_instances,
        VPCZoneIdentifier=[isCfObject(x) for x in subnets],
        Tags=[
            Tag("Name", auto_scaling_group_title, True),
            Tag("Application", app_name, True),
            Tag("S3_DEPLOY_REPO", BOOTSTRAP_S3_DEPLOY_REPO, True),
            Tag("S3_DEPLOY_REPO_PATH", app_name, True),
            Tag("SCRIPT_NAME", BOOTSTRAP_SCRIPT_NAME, True),
            Tag("Environment", ENVIRONMENT_NAME, True),
        ],
    ))

    if not launch_configuration == "":
        asg.LaunchConfigurationName = isCfObject(launch_configuration)

    if not instance == "":
        asg.InstanceId = isCfObject(instance)

    if multiAZ:
        asg.AvailabilityZones = AVAILABILITY_ZONES
    else:
        asg.AvailabilityZones = [AVAILABILITY_ZONES[current_az]]

    if health_check_type == "ELB":
        asg.LoadBalancerNames = [isCfObject(load_balancer)]
        asg.HealthCheckType = health_check_type
        asg.HealthCheckGracePeriod = 300

    if not dependson == "":
        asg.DependsOn = [isCfObject(x) for x in dependson]

    return asg


def add_launch_config(template, key_pair_name, security_groups, image_id, instance_type, userdata=""):
    global num_launch_configs
    num_launch_configs += 1

    non_alphanumeric_title = "LaunchConfiguration" + str(num_launch_configs)
    launch_config_title = trimTitle(non_alphanumeric_title)

    lc = template.add_resource(LaunchConfiguration(
        launch_config_title,
        AssociatePublicIpAddress=True,
        ImageId=image_id,
        InstanceMonitoring=False,
        InstanceType=instance_type,
        KeyName=key_pair_name,
        SecurityGroups=[isCfObject(x) for x in security_groups],
    ))

    if not userdata == "":
        lc.UserData = Base64(userdata)
    return lc


def stack_name_tag():
    return "Ref('AWS::StackName')"


def name_tag(resource_name):
    """Prepend stack name to the given resource name."""
    return Join("", [Ref('AWS::StackName'), '-', resource_name])


def trimTitle(old_title):
    badsymbols = ["-", "*", " ", ".", ",", "/", "\\"]
    for var in badsymbols:
        old_title = old_title.replace(var, "_")

    new_title = inflection.camelize(old_title)
    return new_title


def add_db_subnet_group(template, raw_subnets):
    global num_db_subnet_group
    num_db_subnet_group += 1

    non_alphanumeric_title = "DBSubnetGroup" + str(num_db_subnet_group)
    db_subnet_group_title = trimTitle(non_alphanumeric_title)

    db_subnet_group = template.add_resource(rds.DBSubnetGroup(db_subnet_group_title,
                                                              DBSubnetGroupDescription=db_subnet_group_title,
                                                              SubnetIds=[isCfObject(subnet) for subnet in raw_subnets],
                                                              Tags=Tags(Name=name_tag(db_subnet_group_title))))

    return db_subnet_group


def add_db(template, engine, db_subnet_group, username, password, db_security_groups, db_port="", db_snapshot=""):
    global num_db
    num_db += 1
    global num_db_instance
    num_db_instance += 1

    db_non_alphanumeric_title = "DB" + engine + str(num_db)
    db_title = trimTitle(db_non_alphanumeric_title)

    db_instance_non_alphanumeric_title = "DBInstance" + engine + str(num_db_instance)
    db_instance_title = trimTitle(db_instance_non_alphanumeric_title)

    # Engine matching:mariadb, oracle-se1, oracle-se, oracle-ee, sqlserver-ee, sqlserver-se, sqlserver-ex, sqlserver-web
    if db_port == "":
        if engine == "postgres":
            db_port = 5432
        elif engine == "MySQL":
            db_port = 3306
        elif engine == "aurora":
            db_port = 3306

    db = template.add_resource(rds.DBInstance(db_title,
                                              AllocatedStorage=5,
                                              AllowMajorVersionUpgrade=True,
                                              AutoMinorVersionUpgrade=True,
                                              AvailabilityZone=AVAILABILITY_ZONES[current_az],
                                              BackupRetentionPeriod=0,
                                              # CharacterSetName= (basestring, False),
                                              # DBClusterIdentifier= (basestring, False),
                                              DBInstanceClass="db.t2.micro",
                                              DBInstanceIdentifier=db_instance_title,
                                              DBName=db_title,
                                              # DBParameterGroupName= (basestring, False),
                                              # DBSecurityGroups=isCfObject(db_security_group),
                                              DBSnapshotIdentifier=db_snapshot,
                                              DBSubnetGroupName=isCfObject(db_subnet_group),
                                              Engine=engine,
                                              # EngineVersion= (basestring, False),
                                              # Iops= (validate_iops, False),
                                              # KmsKeyId= (basestring, False),
                                              # LicenseModel= (validate_license_model, False),
                                              MasterUsername=username,
                                              MasterUserPassword=password,
                                              # MultiAZ=False,
                                              # OptionGroupName= (basestring, False),
                                              Port=db_port,
                                              # PreferredBackupWindow= (validate_backup_window, False),
                                              # PreferredMaintenanceWindow= (basestring, False),
                                              PubliclyAccessible=False,
                                              # SourceDBInstanceIdentifier= (basestring, False),
                                              # StorageEncrypted= (boolean, False),
                                              StorageType="standard",
                                              VPCSecurityGroups=[isCfObject(sg) for sg in db_security_groups],
                                              Tags=Tags(Name=name_tag(db_title))))
    return db


def add_r53_hosted_zone(template, vpc, r53_hosted_zone_title=""):

    if r53_hosted_zone_title == "":
        global num_r53_hosted_zone
        num_r53_hosted_zone += 1
        non_alphanumeric_title = "R53HostedZone" + str(num_r53_hosted_zone)
        r53_hosted_zone_title = trimTitle(non_alphanumeric_title)

    r53_hosted_zone_configuration = route53.HostedZoneConfiguration(Comment=r53_hosted_zone_title)
    r53_hosted_zone_vpcs = route53.HostedZoneVPCs(VPCId=isCfObject(vpc), VPCRegion=REGION)
    r53_hosted_zone = template.add_resource(route53.HostedZone(r53_hosted_zone_title,
                                                               HostedZoneConfig=r53_hosted_zone_configuration,
                                                               HostedZoneTags=Tags(Name=name_tag(r53_hosted_zone_title)),
                                                               Name=name_tag(r53_hosted_zone_title) + ".com",
                                                               VPCs=[r53_hosted_zone_vpcs]))

    return r53_hosted_zone


def add_r53_record_set(template, r53_hosted_zone, r53_record_set_name, r53_resource_records, r53_type):
    global num_r53_record_set
    num_r53_record_set += 1

    non_alphanumeric_title = "R53RecordSet" + str(num_r53_record_set)
    r53_record_set_title = trimTitle(non_alphanumeric_title)

    r53_record_set = template.add_resource(route53.RecordSetType(r53_record_set_title,
                                                                 # AliasTarget=(AliasTarget, False),
                                                                 Comment=r53_record_set_title,
                                                                 # Failover=(basestring, False),
                                                                 # GeoLocation=(GeoLocation, False),
                                                                 # HealthCheckId=(basestring, False),
                                                                 HostedZoneId=isCfObject(r53_hosted_zone),
                                                                 # HostedZoneName=(basestring, False),
                                                                 Name=r53_record_set_name,
                                                                 Region=REGION,
                                                                 ResourceRecords=[r53_resource_records],
                                                                 # SetIdentifier=(basestring, False),
                                                                 TTL=300,
                                                                 Type=r53_type))

    return r53_record_set
