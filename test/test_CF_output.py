from nose.tools import *
from amazonia import *
from troposphere import Template


def test_only_three_sydney_azs():
    assert_equals(amazonia_resources.current_az, 0)
    assert_equals(amazonia_resources.AVAILABILITY_ZONES[amazonia_resources.current_az], "ap-southeast-2a")
    switch_availability_zone()
    assert_equals(amazonia_resources.current_az, 1)
    assert_equals(amazonia_resources.AVAILABILITY_ZONES[amazonia_resources.current_az], "ap-southeast-2b")
    switch_availability_zone()
    assert_equals(amazonia_resources.current_az, 2)
    assert_equals(amazonia_resources.AVAILABILITY_ZONES[amazonia_resources.current_az], "ap-southeast-2c")
    switch_availability_zone()
    assert_equals(amazonia_resources.current_az, 0)
    assert_equals(amazonia_resources.AVAILABILITY_ZONES[amazonia_resources.current_az], "ap-southeast-2a")
    switch_availability_zone(2)
    assert_equals(amazonia_resources.current_az, 2)
    assert_equals(amazonia_resources.AVAILABILITY_ZONES[amazonia_resources.current_az], "ap-southeast-2c")

def test_titles_are_alphanumeric():
    title = "abc_bcde-c,d.e*f/g\h_i-j,k.l*m/n\o.p,q.r,s_t-u/v.w_x*y,z."

    title = trimTitle(title)

    assert_equals(title, "AbcBcdeCDEFGHIJKLMNOPQRSTUVWXYZ")


def test_iscfobject():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)

    correcttype = False

    if type(isCfObject(myvpc)) is not str:
        correcttype = True

    assert_equals(correcttype, True)

    correcttype = False

    if type(isCfObject("somestring")) is str:
        correcttype = True

    assert_equals(correcttype, True)


def test_add_vpc():
    template = Template()

    myvpc = add_vpc(template, VPC_CIDR)

    assert_equals(myvpc.CidrBlock, VPC_CIDR)


def test_add_subnet():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    switch_availability_zone(0)

    subnet = add_subnet(template, myvpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)

    assert_equals(subnet.AvailabilityZone, AVAILABILITY_ZONES[current_az])
    assert_equals(subnet.CidrBlock, PUBLIC_SUBNET_AZ1_CIDR)
    assert_equals(subnet.title, PUBLIC_SUBNET_NAME + "1")


def test_add_route_table():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)

    rt = add_route_table(template, myvpc)

    assert_equals(rt.title, "RouteTable1")


def test_add_route_table_subnet_association():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    rt = add_route_table(template, myvpc)
    subnet = add_subnet(template, myvpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)

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


def test_add_route_egress_via_nat():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    rt = add_route_table(template, myvpc)
    subnet = add_subnet(template, myvpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
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
    subnet = add_subnet(template, myvpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
    test_sg = add_security_group(template, myvpc)

    nat = add_nat(template, subnet, "akeypair", test_sg)

    assert_equals(nat.KeyName, "akeypair")
    assert_equals(nat.ImageId, NAT_IMAGE_ID)
    assert_equals(nat.InstanceType, NAT_INSTANCE_TYPE)
    assert_equals(nat.SourceDestCheck, "false")


def test_add_web_instance():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    subnet = add_subnet(template, myvpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
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
    subnet = add_subnet(template, myvpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
    test_sg = add_security_group(template, myvpc)
    web = add_web_instance(template, "akeypair", subnet, test_sg, "test user data")

    this_elb = add_load_balancer(template, [subnet], "HTTP:80/index.html", [test_sg], resources=[web])

    assert_equals(this_elb.CrossZone, "true")
    assert_equals(this_elb.HealthCheck.Target, "HTTP:80/index.html")
    assert_equals(this_elb.HealthCheck.HealthyThreshold, "2")
    assert_equals(this_elb.HealthCheck.UnhealthyThreshold, "5")
    assert_equals(this_elb.HealthCheck.Interval, "15")
    assert_equals(this_elb.HealthCheck.Timeout, "5")
    assert_equals(this_elb.Listeners[0].LoadBalancerPort, "80")
    assert_equals(this_elb.Listeners[0].Protocol, "HTTP")
    assert_equals(this_elb.Listeners[0].InstancePort, "80")
    assert_equals(this_elb.Listeners[0].InstanceProtocol, "HTTP")
    assert_equals(this_elb.Scheme, "internet-facing")


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
    subnet = add_subnet(template, myvpc, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_AZ1_CIDR)
    lc = add_launch_config(template, "akeypair", [test_sg], WEB_IMAGE_ID, WEB_INSTANCE_TYPE)
    switch_availability_zone(0)

    asg = add_auto_scaling_group(template, 4, [subnet], launch_configuration=lc)

    assert_equals(asg.title, "Default" + str(ENVIRONMENT_NAME) + "AutoScalingGroup" + "1")
    assert_equals(asg.MinSize, ASG_MIN_INSTANCES)
    assert_equals(asg.MaxSize, 4)
    assert_equals(asg.AvailabilityZones, [AVAILABILITY_ZONES[current_az]])


def test_add_db_subnet_group():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    subnet1 = add_subnet(template, myvpc, "subnet1", PUBLIC_SUBNET_AZ1_CIDR)
    subnet2 = 'subnet-ab12a1abc'

    dbsubnetgroup = add_db_subnet_group(template, [subnet1, subnet2])

    assert_equals(dbsubnetgroup.title, "DBSubnetGroup1")
    assert_equals(dbsubnetgroup.SubnetIds[1], subnet2)  # unable to test subnet1 here due to difficulties testing Ref.


def test_add_db():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)
    subnet1 = add_subnet(template, myvpc, "subnet1", PUBLIC_SUBNET_AZ1_CIDR)
    subnet2 = 'subnet-ab12a1abc'
    dbsubnetgroup = add_db_subnet_group(template, [subnet1, subnet2])
    sg1 = add_security_group(template, myvpc)
    sg2 = add_security_group(template, myvpc)
    switch_availability_zone(0)

    db = add_db(template, "postgres", dbsubnetgroup, "testuser", "testpassword", [sg1, sg2])

    assert_equals(db.title, "DBpostgres1")
    assert_equals(db.AllocatedStorage, 5)
    assert_equals(db.AllowMajorVersionUpgrade, "true")
    assert_equals(db.AutoMinorVersionUpgrade, "true")
    assert_equals(db.AvailabilityZone, AVAILABILITY_ZONES[current_az])
    assert_equals(db.BackupRetentionPeriod, 0)
    assert_equals(db.DBInstanceClass, "db.t2.micro")
    assert_equals(db.DBInstanceIdentifier, "DBInstancepostgres1")
    assert_equals(db.DBName, db.title)
    assert_equals(db.DBSnapshotIdentifier, "")
    # cannot test dbsubnetgroupname due to difficulties testing Ref
    assert_equals(db.Engine, "postgres")
    assert_equals(db.MasterUsername, "testuser")
    assert_equals(db.MasterUserPassword, "testpassword")
    assert_equals(db.Port, 5432)
    assert_equals(db.PubliclyAccessible, "false")
    assert_equals(db.StorageType, "standard")
    # Cannot test VPCSecurityGroups due to difficulties testing Ref


def test_add_r53_hosted_zone():
    template = Template()
    myvpc = add_vpc(template, VPC_CIDR)

    r53_hosted_zone_manual = add_r53_hosted_zone(template, myvpc, raw_r53_hosted_zone_title="test-hz.com.")
    assert_equals(r53_hosted_zone_manual.Name, "test-hz.com.")


def test_add_r53_record_set():
    template = Template()
    r53_hosted_zone = "test-hz.com."
    r53_record_set_name = "testdns"
    r53_resource_records = "10.0.0.5"
    r53_type = "A"

    r53_record_set = add_r53_record_set(template, r53_hosted_zone, r53_record_set_name, r53_resource_records, r53_type)

    assert_equals(r53_record_set.ResourceRecords, ["10.0.0.5"])
    assert_equals(r53_record_set.Type, "A")


def test_add_cd_application():
    template = Template()
    cd_application = add_cd_application(template, app_name="testapp")

    assert_equals(cd_application.ApplicationName, "testapp")


def test_add_cd_deploygroup():
    template = Template()
    auto_scaling_group = "deploygrp-TestappEXPERIMENTALAutoScalingGroup1-1Q4F92R4M768L"

    cd_deploygroup = add_cd_deploygroup(template, "testapp", auto_scaling_group, service_role_arn="arn:aws:iam::658695688407:role/CodeDeploy")

    assert_equals(cd_deploygroup.ApplicationName, "testapp"),
    assert_equals(cd_deploygroup.ServiceRoleArn, "arn:aws:iam::658695688407:role/CodeDeploy"),
    assert_equals(cd_deploygroup.AutoScalingGroups, ["deploygrp-TestappEXPERIMENTALAutoScalingGroup1-1Q4F92R4M768L"])
