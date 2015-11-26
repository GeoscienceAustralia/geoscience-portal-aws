# pylint: disable=too-many-arguments

"""

The functions in this module generate cloud formation scripts that install common AWS environments and components

"""

from troposphere import Ref, Tags, Join, Base64
import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb
import sys

NAT_IMAGE_ID = "ami-893f53b3"
NAT_INSTANCE_TYPE = "t2.micro"
NAT_IP_ADDRESS="10.0.0.100"
SYSTEM_NAME="TestApplication"
ENVIRONMENT_NAME="Experimental"
AVAILABILITY_ZONES = ["ap-southeast-2a", "ap-southeast-2b"]
WEB_IMAGE_ID = "ami-c11856fb"
WEB_INSTANCE_TYPE= "t2.small"

#CIDRs
PUBLIC_GA_GOV_AU_CIDR = '192.104.44.129/32'
VPC_CIDR = "10.0.0.0/16" 
PUBLIC_SUBNET_AZ1_CIDR = "10.0.0.0/24"
PUBLIC_SUBNET_AZ2_CIDR = "10.0.10.0/24"
PRIVATE_SUBNET_AZ1_CIDR = "10.0.1.0/24"
PRIVATE_SUBNET_AZ2_CIDR = "10.0.11.0/24"
PUBLIC_CIDR = "0.0.0.0/0"
PUBLIC_SUBNET_NAME = "PublicSubnet"
PRIVATE_SUBNET_NAME = "PrivateSubnet"

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
num_load_balancers = 0
num_web_instances = 0
num_web_security_groups = 0

def switch_availability_zone():
    """ A simple function to switch Availability zones. """
    global current_az
    if current_az == 0:
        current_az = 1
    else:
        current_az = 0


def add_vpc(template, cidr):
    """Create a VPC resource and add it to the given template."""
    global num_vpcs
    num_vpcs = num_vpcs + 1
    vpc_title = "VPC" + str(num_vpcs)

    vpc = template.add_resource(ec2.VPC(vpc_title,
                                        CidrBlock=cidr,
                                        Tags=Tags(Name=name_tag(vpc_title),
                                        Environment=ENVIRONMENT_NAME)))  
    return vpc


def add_subnet(template, vpc, name, cidr):
    global num_subnets
    num_subnets += 1

    title = name + str(num_subnets)
    public_subnet = template.add_resource(ec2.Subnet(title,
                                                     AvailabilityZone=AVAILABILITY_ZONES[current_az],
                                                     VpcId=Ref(vpc.title),
                                                     CidrBlock=cidr,
                                                     Tags=Tags(Name=name_tag(title), Environment=ENVIRONMENT_NAME)))
    return public_subnet

								
def add_route_table(template, vpc, subnet, route_type=""):

	global num_route_tables
	num_route_tables = num_route_tables + 1

	# create the route table in the VPC
	route_table_id = route_type + "RouteTable" + str(num_route_tables)
	route_table = template.add_resource(ec2.RouteTable(route_table_id,
                                                           VpcId=Ref(vpc.title),
                                                           Tags=Tags(Name=name_tag(route_table_id)),))
	
	# Associate the route table with the subnet
	template.add_resource(ec2.SubnetRouteTableAssociation(
		route_table_id + "Association",
		SubnetId=Ref(subnet.title),
		RouteTableId=Ref(route_table),
	))
	return route_table
	

def add_internet_gateway(template, vpc):
	global num_internet_gateways
	num_internet_gateways = num_internet_gateways + 1
	internet_gateway_title = "InternetGateway" + str(num_internet_gateways)

        internet_gateway = template.add_resource(ec2.InternetGateway(internet_gateway_title,
                                                                     Tags=Tags(Name=name_tag(internet_gateway_title),
                                                                               Environment=ENVIRONMENT_NAME)

        ))

        attachment_title = internet_gateway_title + "Attachment"
        template.add_resource(ec2.VPCGatewayAttachment(attachment_title,
                                                       VpcId=Ref(vpc.title),
                                                       InternetGatewayId=Ref(internet_gateway.title),
        ))
        return internet_gateway


def add_route_ingress_via_gateway(template, route_table, internet_gateway, cidr):
	global num_routes 
	num_routes = num_routes + 1
	template.add_resource(ec2.Route(
		"InboundRoute" + str(num_routes),
		GatewayId=Ref(internet_gateway.title),
		RouteTableId=Ref(route_table.title),
		DestinationCidrBlock=cidr))


def add_route_egress_via_NAT(template, route_table, nat):
	global num_routes 
	num_routes = num_routes + 1

        template.add_resource(ec2.Route("OutboundRoute" + str(num_routes),
                                        InstanceId=Ref(nat.title),
                                        RouteTableId=Ref(route_table.title),
                                        DestinationCidrBlock="0.0.0.0/0",
        ))

        
def add_security_group(template, vpc):
    global num_security_groups 
    num_security_groups += 1
    sg_title = "SecurityGroup" + str(num_security_groups)

    sg = template.add_resource(ec2.SecurityGroup(sg_title,
                                                 GroupDescription="Security group",
                                                 VpcId=Ref(vpc.title),
                                                 Tags=Tags(Name=name_tag(sg_title))))

    return sg     



def add_security_group_ingress(template, security_group, protocol, from_port, to_port, cidr):

    global num_ingress_rules
    num_ingress_rules += 1
    title = security_group.title + 'Ingress' + protocol + str(num_ingress_rules)
    template.add_resource(ec2.SecurityGroupIngress(title,
                                                   IpProtocol=protocol,
                                                   FromPort=from_port,
                                                   ToPort=to_port,
                                                   GroupId=Ref(security_group.title),
                                                   CidrIp=cidr))
    return template


def add_nat(template, public_subnet, key_pair_name, security_group, natIP=NAT_IP_ADDRESS):
    global num_nats
    num_nats += 1
    nat_title = "NAT" + str(num_nats)
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
        #PrivateIpAddress=natIP,
        Tags=Tags(
            Name=name_tag(nat_title),
        ),
    ))
    return nat

def add_web_instance(template, key_pair_name, subnet, security_group, userdata):
    global num_web_instances
    num_web_instances += 1

    instance_title = "WebServer" + str(num_web_instances)

    instance = template.add_resource(ec2.Instance(
        instance_title,
        InstanceType=WEB_INSTANCE_TYPE,
        KeyName=key_pair_name,
        SourceDestCheck=False,
        ImageId=WEB_IMAGE_ID,
        NetworkInterfaces=[ec2.NetworkInterfaceProperty(
                                                        GroupSet=[Ref(security_group.title)],
                                                        AssociatePublicIpAddress=True,
                                                        DeviceIndex="0",
                                                        DeleteOnTermination=True,
                                                        SubnetId=Ref(subnet.title),
        )],
        Tags=Tags(
            Name=name_tag(instance_title),
        ),
        UserData=Base64(userdata),
    ))
    return instance


def add_load_balancer(template, instances, subnets, healthcheck_target, security_groups):
    global num_load_balancers
    num_load_balancers += 1

    elb_title = "ElasticLoadBalancer" + str(num_load_balancers)
    return_elb = template.add_resource(elb.LoadBalancer(
        elb_title,
        CrossZone=True,
        Instances=[Ref(instances[0]),Ref(instances[1])],
        HealthCheck=elb.HealthCheck(
                                    Target=healthcheck_target,
                                    HealthyThreshold="10",
                                    UnhealthyThreshold="2",
                                    Interval="30",
                                    Timeout="5",
        ),
        Listeners=[elb.Listener(
                                LoadBalancerPort="80",
                                Protocol="HTTP",
                                InstancePort="80",
                                InstanceProtocol="HTTP",
        )],
        Scheme="internet-facing",
        SecurityGroups=[Ref(security_groups[0])],
        Subnets=[Ref(subnets[0]),Ref(subnets[1])],
        Tags=Tags(
            Name=name_tag(elb_title),
        ),
    ))
    return return_elb


def stack_name_tag():
    return "Ref('AWS::StackName')" 

def name_tag(resource_name):
    """Prepend stack name to the given resource name."""
    return Join("", [Ref('AWS::StackName'), '-', resource_name])

def private_subnet(template, name):
    """Extract and return the specified subnet resource from the given template."""
    return template.resources[name]







