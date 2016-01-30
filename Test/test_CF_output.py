from nose.tools import *
from amazonia import *
from troposphere import Template


def test_only_two_AZs():
    assert_equals(amazonia_resources.current_az, 0)
    switch_availability_zone()
    assert_equals(amazonia_resources.current_az, 1)
    switch_availability_zone()
    assert_equals(amazonia_resources.current_az, 0)

def test_titles_are_alphanumeric():
    title = "abc_bcde-c,d.e*f/g\h_i-j,k.l*m/n\o.p,q.r,s_t-u/v.w_x*y,z"

    title = trimTitle(title)

    assert_equals(title, "AbcBcdeCDEFGHIJKLMNOPQRSTUVWXYZ")

def test_add_VPC():
    template = Template()

    myvpc = add_vpc(template, VPC_CIDR)

    assert_equals(myvpc.CidrBlock, VPC_CIDR)

def test_add_subnet():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)

    subnet = add_subnet(template, myvpc, "Public", PUBLIC_SUBNET_AZ1_CIDR)

    assert_equals(subnet.AvailabilityZone, AVAILABILITY_ZONES[current_az])
    assert_equals(subnet.CidrBlock, PUBLIC_SUBNET_AZ1_CIDR)
    assert_equals(subnet.title, "Public1")

def test_add_route_table():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)

    rt = add_route_table(template, myvpc)

    assert_equals(rt.title, "RouteTable1")

def test_add_route_table_subnet_association():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    rt = add_route_table(template, myvpc)
    subnet = add_subnet(template, myvpc, "Public", PUBLIC_SUBNET_AZ1_CIDR)

    rta = add_route_table_subnet_association(template, rt, subnet)

    assert_equals(rta.title, rt.title + "Association1")

def test_add_internet_gateway():
    template = Template()

    igw = add_internet_gateway(template)

    assert_equals(igw.title, "InternetGateway1")

def test_add_internet_gateway_attachment():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    igw = add_internet_gateway(template)

    igwa = add_internet_gateway_attachment(template, myvpc, igw)

    assert_equals(igwa.title, igw.title + "Attachment")

def test_add_route_ingress_via_gateway():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    rt = add_route_table(template, myvpc)
    igw = add_internet_gateway(template)

    route = add_route_ingress_via_gateway(template, rt, igw, VPC_CIDR)

    assert_equals(route.DestinationCidrBlock, VPC_CIDR)

def test_add_route_egress_via_NAT():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    rt = add_route_table(template, myvpc)
    subnet = add_subnet(template, myvpc, "Public", PUBLIC_SUBNET_AZ1_CIDR)
    test_sg = add_security_group(template, myvpc)
    nat = add_nat(template, subnet, "akeypair", test_sg)

    route = add_route_egress_via_NAT(template, rt, nat)

    assert_equals(route.DestinationCidrBlock, PUBLIC_CIDR)

def test_add_security_group():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)

    test_sg = add_security_group(template, myvpc)

    assert_equals(test_sg.GroupDescription, "Security group")
    assert_equals(test_sg.title, "SecurityGroup2")

def test_add_security_group_ingress():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    test_sg = add_security_group(template, myvpc)

    ingress = add_security_group_ingress(template, test_sg, "TCP", "12", "34", cidr=PUBLIC_CIDR)

    assert_equals(ingress.IpProtocol, "TCP")
    assert_equals(ingress.FromPort, "12")
    assert_equals(ingress.ToPort, "34")
    assert_equals(ingress.CidrIp, PUBLIC_CIDR)

def test_add_security_group_egress():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    test_sg = add_security_group(template, myvpc)

    egress = add_security_group_egress(template, test_sg, "TCP", "12", "34", cidr=PUBLIC_CIDR)

    assert_equals(egress.IpProtocol, "TCP")
    assert_equals(egress.FromPort, "12")
    assert_equals(egress.ToPort, "34")
    assert_equals(egress.CidrIp, PUBLIC_CIDR)

def test_add_nat():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    subnet = add_subnet(template, myvpc, "Public", PUBLIC_SUBNET_AZ1_CIDR)
    test_sg = add_security_group(template, myvpc)

    nat = add_nat(template, subnet, "akeypair", test_sg)

    assert_equals(nat.KeyName, "akeypair")
    assert_equals(nat.ImageId, NAT_IMAGE_ID)
    assert_equals(nat.InstanceType, NAT_INSTANCE_TYPE)
    assert_equals(nat.SourceDestCheck, "false")

def test_add_web_instance():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    subnet = add_subnet(template, myvpc, "Public", PUBLIC_SUBNET_AZ1_CIDR)
    test_sg = add_security_group(template, myvpc)

    web = add_web_instance(template, "akeypair", subnet, test_sg, "test user data")

    assert_equals(web.InstanceType, WEB_INSTANCE_TYPE)
    assert_equals(web.KeyName, "akeypair")
    assert_equals(web.SourceDestCheck, "false")
    assert_equals(web.ImageId, WEB_IMAGE_ID)
    assert_equals(web.NetworkInterfaces[0].AssociatePublicIpAddress, "true")

def test_add_load_balancer():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    subnet = add_subnet(template, myvpc, "Public", PUBLIC_SUBNET_AZ1_CIDR)
    test_sg = add_security_group(template, myvpc)
    web = add_web_instance(template, "akeypair", subnet, test_sg, "test user data")

    elb = add_load_balancer(template, [subnet], "HTTP:80/index.html", [test_sg], [web])

    assert_equals(elb.CrossZone, "true")
    assert_equals(elb.HealthCheck.Target, "HTTP:80/index.html")
    assert_equals(elb.HealthCheck.HealthyThreshold, "2")
    assert_equals(elb.HealthCheck.UnhealthyThreshold, "5")
    assert_equals(elb.HealthCheck.Interval, "15")
    assert_equals(elb.HealthCheck.Timeout, "5")
    assert_equals(elb.Listeners[0].LoadBalancerPort, "80")
    assert_equals(elb.Listeners[0].Protocol, "HTTP")
    assert_equals(elb.Listeners[0].InstancePort, "80")
    assert_equals(elb.Listeners[0].InstanceProtocol, "HTTP")
    assert_equals(elb.Scheme, "internet-facing")

def test_add_launch_config():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    test_sg = add_security_group(template, myvpc)

    lc = add_launch_config(template, "akeypair", [test_sg], WEB_IMAGE_ID, WEB_INSTANCE_TYPE)

    assert_equals(lc.AssociatePublicIpAddress, "true")
    assert_equals(lc.ImageId, WEB_IMAGE_ID)
    assert_equals(lc.InstanceMonitoring, "false")
    assert_equals(lc.InstanceType, WEB_INSTANCE_TYPE)
    assert_equals(lc.KeyName, "akeypair")

def test_add_auto_scaling_group():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    test_sg = add_security_group(template, myvpc)
    subnet = add_subnet(template, myvpc, "Public", PUBLIC_SUBNET_AZ1_CIDR)
    lc = add_launch_config(template, "akeypair", [test_sg], WEB_IMAGE_ID, WEB_INSTANCE_TYPE)

    asg = add_auto_scaling_group(template, 4, [subnet], launch_configuration=lc)

    assert_equals(asg.title,"Default" + str(ENVIRONMENT_NAME) + "AutoScalingGroup" + "1")
    assert_equals(asg.MinSize, ASG_MIN_INSTANCES)
    assert_equals(asg.MaxSize, 4)
    assert_equals(asg.AvailabilityZones, [AVAILABILITY_ZONES[current_az]])

# TODO Test classes from ctemplates to ensure certain objects exist? eg publicsubnet1, publicsubnet2, internetgateway etc etc
