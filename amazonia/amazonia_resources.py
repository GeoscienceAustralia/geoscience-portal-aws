# pylint: disable=too-many-arguments, line-too-long

"""

The functions in this module generate cloud formation scripts that install common AWS environments and components

"""

from troposphere import Ref, Tags, Join, Base64, GetAtt, ec2
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration, Tag
import troposphere.elasticloadbalancing as elb
import inflection

NAT_IMAGE_ID = "ami-893f53b3"
NAT_INSTANCE_TYPE = "t2.micro"
NAT_IP_ADDRESS = "10.0.0.100"
SYSTEM_NAME = "TestApplication"
ENVIRONMENT_NAME = "EXPERIMENTAL"
AVAILABILITY_ZONES = ["ap-southeast-2a", "ap-southeast-2b"]
WEB_IMAGE_ID = "ami-910623f2" # OLD AMI: "ami-c11856fb"  # BASE AMI: "ami-ba6f4ad9"
WEB_INSTANCE_TYPE = "t2.small"
ASG_MIN_INSTANCES = 1

# CIDRs
PUBLIC_GA_GOV_AU_CIDR = '192.104.44.129/32'
VPC_CIDR = "10.0.0.0/16"
PUBLIC_SUBNET_AZ1_CIDR = "10.0.0.0/24"
PUBLIC_SUBNET_AZ2_CIDR = "10.0.10.0/24"
PRIVATE_SUBNET_AZ1_CIDR = "10.0.1.0/24"
PRIVATE_SUBNET_AZ2_CIDR = "10.0.11.0/24"
PUBLIC_CIDR = "0.0.0.0/0"
PUBLIC_SUBNET_NAME = "PublicSubnet"
PRIVATE_SUBNET_NAME = "PrivateSubnet"

# WEB SERVER BOOTSTRAP SCRIPTS
WEB_SERVER_AZ1_USER_DATA = "#!/bin/sh\n"
WEB_SERVER_AZ1_USER_DATA += "yum -y install httpd && chkconfig httpd on\n"
WEB_SERVER_AZ1_USER_DATA += "/etc/init.d/httpd start && yum -y install git\n"
WEB_SERVER_AZ1_USER_DATA += "git clone https://github.com/budawangbill/webserverconfig.git\n"
WEB_SERVER_AZ1_USER_DATA += "cp webserverconfig/testAZ1.html /var/www/html/test.html\n"
WEB_SERVER_AZ1_USER_DATA += "sed -i '/Listen 80/a Listen 8080' /etc/httpd/conf/httpd.conf\n"
WEB_SERVER_AZ1_USER_DATA += "service httpd restart"

WEB_SERVER_AZ2_USER_DATA = "#!/bin/sh\n"
WEB_SERVER_AZ2_USER_DATA += "yum -y install httpd && chkconfig httpd on\n"
WEB_SERVER_AZ2_USER_DATA += "/etc/init.d/httpd start && yum -y install git\n"
WEB_SERVER_AZ2_USER_DATA += "git clone https://github.com/budawangbill/webserverconfig.git\n"
WEB_SERVER_AZ2_USER_DATA += "cp webserverconfig/testAZ2.html /var/www/html/test.html\n"
WEB_SERVER_AZ2_USER_DATA += "sed -i '/Listen 80/a Listen 8080' /etc/httpd/conf/httpd.conf\n"
WEB_SERVER_AZ2_USER_DATA += "service httpd restart"

# Handler for switching Availability Zones
current_az = 0

# Bootstrap variables for instances & auto scaling groups
BOOTSTRAP_S3_DEPLOY_REPO = "smallest-bucket-in-history"
BOOTSTRAP_SCRIPT_NAME = "bootstrap_custom_script.sh"

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

    public_subnet = template.add_resource(ec2.Subnet(subnet_title,
                                                     AvailabilityZone=AVAILABILITY_ZONES[current_az],
                                                     VpcId=Ref(vpc.title),
                                                     CidrBlock=cidr,
                                                     Tags=Tags(Name=name_tag(subnet_title),
                                                               Environment=ENVIRONMENT_NAME)))
    return public_subnet

def add_route_table(template, vpc, route_type=""):
    global num_route_tables
    num_route_tables = num_route_tables + 1

    non_alphanumeric_title = route_type + "RouteTable" + str(num_route_tables)
    route_table_title = trimTitle(non_alphanumeric_title)

    route_table = template.add_resource(ec2.RouteTable(route_table_title,
                                                       VpcId=Ref(vpc.title),
                                                       Tags=Tags(Name=name_tag(route_table_title)),
                                                      ))
    return route_table

def add_route_table_subnet_association(template, route_table, subnet):
    global num_route_table_associations
    num_route_table_associations += 1

    # Associate the route table with the subnet
    route_table_association = template.add_resource(ec2.SubnetRouteTableAssociation(
        route_table.title + "Association" + str(num_route_table_associations),
        SubnetId=Ref(subnet.title),
        RouteTableId=Ref(route_table.title),
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

    attachment_title = internet_gateway.title + "Attachment"
    gateway_attachment = template.add_resource(ec2.VPCGatewayAttachment(attachment_title,
                                                                        VpcId=Ref(vpc.title),
                                                                        InternetGatewayId=Ref(internet_gateway.title),
                                                                       ))

    return gateway_attachment

def add_route_ingress_via_gateway(template, route_table, internet_gateway, cidr, dependson = ""):
    global num_routes
    num_routes += 1
    route = template.add_resource(ec2.Route(
        "InboundRoute" + str(num_routes),
        GatewayId=Ref(internet_gateway.title),
        RouteTableId=Ref(route_table.title),
        DestinationCidrBlock=cidr
    ))

    if not dependson == "":
        route.DependsOn = [x.title for x in dependson]

    return route

def add_route_egress_via_NAT(template, route_table, nat, dependson=""):
    global num_routes
    num_routes += 1

    route = template.add_resource(ec2.Route("OutboundRoute" + str(num_routes),
                                    InstanceId=Ref(nat.title),
                                    RouteTableId=Ref(route_table.title),
                                    DestinationCidrBlock=PUBLIC_CIDR,
                                   ))

    if not dependson == "":
        route.DependsOn = [x.title for x in dependson]

    return route

def add_security_group(template, vpc):
    global num_security_groups
    num_security_groups += 1

    non_alphanumeric_title = "SecurityGroup" + str(num_security_groups)
    sg_title = trimTitle(non_alphanumeric_title)

    sg = template.add_resource(ec2.SecurityGroup(sg_title,
                                                 GroupDescription="Security group",
                                                 VpcId=Ref(vpc.title),
                                                 Tags=Tags(Name=name_tag(sg_title))))

    return sg

def add_security_group_ingress(template, security_group, protocol, from_port, to_port, cidr="", source_security_group=""):

    global num_ingress_rules
    num_ingress_rules += 1

    if not protocol == "-1":
        non_alphanumeric_title = security_group.title + 'Ingress' + protocol + str(num_ingress_rules)
    else:
        non_alphanumeric_title = security_group.title + 'IngressAll' + str(num_ingress_rules)

    ingress_title = trimTitle(non_alphanumeric_title)

    sg_ingress = template.add_resource(ec2.SecurityGroupIngress(ingress_title,
                                                                IpProtocol=protocol,
                                                                FromPort=from_port,
                                                                ToPort=to_port,
                                                                GroupId=Ref(security_group.title)
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

    if not protocol == "-1":
        non_alphanumeric_title = security_group.title + 'Egress' + protocol + str(num_egress_rules)
    else:
        non_alphanumeric_title = security_group.title + 'EgressAll' + str(num_egress_rules)

    egress_title = trimTitle(non_alphanumeric_title)

    sg_egress = template.add_resource(ec2.SecurityGroupEgress(egress_title,
                                                              IpProtocol=protocol,
                                                              FromPort=from_port,
                                                              ToPort=to_port,
                                                              GroupId=Ref(security_group.title)
                                                             ))

    if not destination_security_group == "":
        sg_egress.DestinationSecurityGroupId = GetAtt(destination_security_group.title, "GroupId")
    else:
        if not cidr == "":
            sg_egress.CidrIp = cidr

    return sg_egress

def add_nat(template, public_subnet, key_pair_name, security_group):
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
            GroupSet=[Ref(security_group.title)],
            AssociatePublicIpAddress=True,
            DeviceIndex="0",
            DeleteOnTermination=True,
            SubnetId=Ref(public_subnet.title),
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
            GroupSet=[Ref(security_group.title)],
            AssociatePublicIpAddress=public,
            DeviceIndex="0",
            DeleteOnTermination=True,
            SubnetId=Ref(subnet.title),
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

def add_load_balancer(template, subnets, healthcheck_target, security_groups, resources="", dependson= ""):
    global num_load_balancers
    num_load_balancers += 1

    non_alphanumeric_title = "ElasticLoadBalancer" + str(num_load_balancers)
    elb_title = trimTitle(non_alphanumeric_title)

    return_elb = template.add_resource(elb.LoadBalancer(
        elb_title,
        CrossZone=True,
        HealthCheck=elb.HealthCheck(
            Target=healthcheck_target,
            HealthyThreshold="2",
            UnhealthyThreshold="5",
            Interval="15",
            Timeout="5",
        ),
        Listeners=[elb.Listener(
            LoadBalancerPort="80",
            Protocol="HTTP",
            InstancePort="80",
            InstanceProtocol="HTTP",
        )],
        Scheme="internet-facing",
        SecurityGroups=[Ref(x) for x in security_groups],
        Subnets=[Ref(x) for x in subnets],
        Tags=Tags(
            Name=name_tag(elb_title),
        ),
    ))

    if not resources == "":
        return_elb.Instances = [Ref(x) for x in resources]

    if not dependson == "":
        return_elb.DependsOn = [x.title for x in dependson]

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
        VPCZoneIdentifier=[Ref(x) for x in subnets],
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
        asg.LaunchConfigurationName = Ref(launch_configuration.title)

    if not instance == "":
        asg.InstanceId = Ref(instance.title)

    if multiAZ:
        asg.AvailabilityZones = AVAILABILITY_ZONES
    else:
        asg.AvailabilityZones = [AVAILABILITY_ZONES[current_az]]

    if health_check_type == "ELB":
        asg.LoadBalancerNames = [Ref(load_balancer.title)]
        asg.HealthCheckType = health_check_type
        asg.HealthCheckGracePeriod = 300

    if not dependson == "":
        asg.DependsOn = [x.title for x in dependson]

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
        SecurityGroups=[Ref(x) for x in security_groups],
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
    old_title = old_title.replace("-", "_")
    old_title = old_title.replace("*", "_")
    old_title = old_title.replace(" ", "_")
    old_title = old_title.replace(".", "_")
    old_title = old_title.replace(",", "_")
    old_title = old_title.replace("/", "_")
    old_title = old_title.replace("\\", "_")
    new_title = inflection.camelize(old_title)
    return new_title
