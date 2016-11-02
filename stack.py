# pylint: disable=missing-docstring, invalid-name, line-too-long, fixme

"""Geoscience Portal AWS CloudFormation Stack Definition
"""

import glob
import os
import random
import string
from   subprocess import call
import sys

import boto3

from   troposphere import Base64, Join, Ref, Tags
from   troposphere import cloudformation as cf
import troposphere.ec2 as ec2
import troposphere.autoscaling as auto
import troposphere.elasticloadbalancing as elb

from amazonia.cftemplates import SingleAZenv
from amazonia.amazonia_resources import name_tag, add_security_group_ingress

PUBLIC_GA_GOV_AU_PTR = '192.104.44.129'
IMAGE_ID = "ami-48d38c2b"
KEY_PAIR_NAME = "lazar@work"
GA_PUBLIC_NEXUS = "http://maven-int.ga.gov.au/nexus/service/local/artifact/maven/redirect?r=public"
MVN_SNAPSHOTS = "geoscience-portal/mvn-snapshot/"

def _generate_password():
    return ''.join(random.sample(string.ascii_letters + string.digits, 10))

POSTGRES_SUPERUSER_PASSWORD = _generate_password()
GEONETWORK_DB_PASSWORD = _generate_password()

stack_id = Ref("AWS::StackId")
stack_name = Ref("AWS:StackName")
region = Ref("AWS::Region")

class GeosciencePortalStack(SingleAZenv):
    def __init__(self):
        super(GeosciencePortalStack, self).__init__(KEY_PAIR_NAME)

        security_group = self.add_resource(webserver_security_group(self.vpc))
        add_http_ingress(self, security_group)
        add_tomcat_ingress(self, security_group)
        add_icmp_ingress(self, security_group)
        add_ssh_ingress(self, security_group)

        nat_wait_handle = self.add_resource(cf.WaitConditionHandle("natWaitHandle"))
        wait_title = "WaitFor" + self.nat.title
        nat_wait = self.add_resource(cf.WaitCondition(
            wait_title,
            Handle=Ref(nat_wait_handle),
            DependsOn=self.nat.title,
            Timeout="300",
        ))

        webserver_launch_config = make_webserver(nat_wait, security_group)
        self.add_resource(webserver_launch_config)

        with open("nat-init.sh", "r") as user_data:
            self.nat.UserData = Base64(Join("", ["#!/bin/bash\n", "signal_url='", Ref(nat_wait_handle), "'\n", user_data.read()]))

        load_balancer_title = system_prefix() + "LoadBalancer"
        load_balancer = self.add_resource(elb.LoadBalancer(
            load_balancer_title,
            Tags=Tags(
                Name=name_tag(load_balancer_title),
            ),
            # ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
            #     Enabled=True,
            #     Timeout=120,
            # ),
            Subnets=[Ref(self.public_subnet)],
            HealthCheck=elb.HealthCheck(
                Target="HTTP:8080/gmap.html",
                HealthyThreshold="2",
                UnhealthyThreshold="10",
                Interval="300",
                Timeout="30",
            ),
            Listeners=[
                elb.Listener(
                    LoadBalancerPort="80",
                    InstancePort="8080",
                    Protocol="HTTP",
                    InstanceProtocol="HTTP",
                ),
            ],
            SecurityGroups=[Ref(elb_security_group(self))],
            LoadBalancerName=load_balancer_title
        ))

        ag_title = "WebServer"
        self.add_resource(auto.AutoScalingGroup(
            ag_title,
            HealthCheckType="ELB",
            HealthCheckGracePeriod="300",
            LaunchConfigurationName=Ref(webserver_launch_config),
            MinSize=1,
            MaxSize=1,
            VPCZoneIdentifier=[Ref(self.private_subnet)],
            LoadBalancerNames=[Ref(load_balancer)],
            Tags=[auto.Tag("Name", name_tag(ag_title), True)],
        ))

def geoscience_portal_version():
    return sys.argv[1]

def geoscience_portal_geonetwork_version():
    return sys.argv[2]

def environment():
    return sys.argv[3]

def system_prefix():
    return "GeosciencePortal" + environment()

def get_nexus_artifact_url(group_id, artifact_id, version):
    os.chdir("target")
    war_filename = max(glob.iglob("*.war"), key=os.path.getctime)
    #war_filename = artifact_id + "-" + version + ".war"
    call(["aws", "s3", "cp", war_filename, "s3://" + MVN_SNAPSHOTS, "--profile", "geoscience-portal", "--quiet", "--acl", "public-read"])
    os.chdir("..")

    s3 = boto3.client("s3")
    bucket, folder = tuple(MVN_SNAPSHOTS.split("/", 1))
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": bucket,
            "Key": folder + war_filename,
        },
        ExpiresIn=31622400, # TODO: a year
        )

def get_geoscience_portal_war_url():
    return get_nexus_artifact_url("au.gov.ga", "geoscience-portal", geoscience_portal_version())

def get_geoscience_portal_geonetwork_war_url():
    return get_nexus_artifact_url("au.gov.ga", "geoscience-portal-geonetwork", geoscience_portal_geonetwork_version())

def make_webserver(nat_wait, security_group):
    instance_id = "WebserverLaunchConfig"
    instance = auto.LaunchConfiguration(
        instance_id,
        ImageId=IMAGE_ID,
        InstanceType="t2.medium",
        KeyName=KEY_PAIR_NAME,
        SecurityGroups=[Ref(security_group)],
        DependsOn=nat_wait.title,
        Metadata=cf.Metadata(
            cf.Init(
                cf.InitConfigSets(
                    default=["on_create", {"ConfigSet": "update"}],
                    update=["on_update"]
                ),
                on_create=cf.InitConfig(
                    packages={
                        "yum": {
                            "tomcat7": [],
                            "wget": [],
                            "postgresql92-server": [],
                            "java-1.8.0-openjdk": [],
                            # "python-pip": [], TODO: leave out for now
                            # "python34": [],
                            "unzip": [],
                        }
                    },
                    files=cf.InitFiles({
                        "/etc/cfn/cfn-hup.conf": cf.InitFile(
                            content=Join('', [
                                "[main]\n",
                                "stack=", stack_id, "\n",
                                "region=", region, "\n",
                                "interval=1\n",
                            ]),
                            mode="000400",
                            owner="root",
                            group="root"
                        ),
                        "/etc/cfn/hooks.d/cfn-auto-reloader.conf": cf.InitFile(
                            content=Join("", [
                                "[cfn-auto-reloader-hook]\n",
                                "triggers=post.update\n",
                                "path=Resources.", instance_id, ".Metadata.AWS::CloudFormation::Init\n",
                                "action=/opt/aws/bin/cfn-init",
                                " --stack ", stack_id,
                                " --resource ", instance_id,
                                " --region ", region,
                                " -c update\n",
                                "runas=root\n"
                            ]),
                        ),
                        "/root/.pgpass": cf.InitFile(
                            content="localhost:5432:*:postgres:" + POSTGRES_SUPERUSER_PASSWORD,
                            mode="0600",
                        ),
                        "/var/lib/pgsql92/password": cf.InitFile(
                            content=POSTGRES_SUPERUSER_PASSWORD,
                            owner="postgres",
                            mode="0600",
                        ),
                    }),
                    commands={
                        "00-disable-webapp-auto-deployment": {
                            "command": "sed -i 's/autoDeploy=\"true\"/autoDeploy=\"false\"/' /usr/share/tomcat7/conf/server.xml"
                        },
                        "20-allow-sudo-without-tty": {
                            "command": "sed -i '/Defaults    requiretty/s/^/#/g' /etc/sudoers"
                        },
                        "30-init-postgres": {
                            "command": "sudo -u postgres initdb -D /var/lib/pgsql92/data -A md5 --pwfile=/var/lib/pgsql92/password"
                        },
                        "40-persist-hostname": {
                            "command": "sed -i 's/HOSTNAME=localhost.localdomain/HOSTNAME=portal-dev.localdomain/' /etc/sysconfig/network"
                        },
                        "50-set-hostname": {
                            "command": "hostname portal-dev"
                        },
                        "60-set-hostname-resolution": {
                            "command": "echo '127.0.0.1   portal-dev portal-dev.localdomain localhost localhost.localdomain' > /etc/hosts"
                        },
                        # "40-install-pip3": {
                        #     "command": "wget -O - https://bootstrap.pypa.io/get-pip.py | python3.4 && ln -s /usr/bin/python3.4 /usr/bin/python3"
                        # },
                        # "42-install-python3-urllib3": {
                        #     "command": "pip3 install urllib3"
                        # },
                    },
                    services={
                        "sysvinit": cf.InitServices({
                            "postgresql92": cf.InitService(
                                enabled=True,
                                ensureRunning=True,
                            ),
                            "tomcat7": cf.InitService(
                                enabled=True,
                                ensureRunning=True,
                            ),
                            "cfn-hup": cf.InitService(
                                enabled=True,
                                ensureRunning=True,
                                files=[
                                    "/etc/cfn/cfn-hup.conf",
                                    "/etc/cfn/hooks.d/cfn-auto-reloader.conf"
                                ],
                            ),
                        }),
                    },
                ),
                on_update=cf.InitConfig(
                    files=cf.InitFiles({
                        "/usr/share/tomcat7/webapps/ROOT.war": cf.InitFile(
                            source=get_geoscience_portal_war_url(),
                            owner="tomcat",
                            group="tomcat",
                        ),
                        "/usr/share/tomcat7/webapps/geonetwork.war": cf.InitFile(
                            source=get_geoscience_portal_geonetwork_war_url(),
                            owner="tomcat",
                            group="tomcat",
                        ),
                    }),
                    commands={
                        "00-stop-tomcat": {
                            "command": "service tomcat7 stop"
                        },
                        "10-setup-geonetwork-database": {
                            "command": "unzip -p /usr/share/tomcat7/webapps/geonetwork.war WEB-INF/classes/geonetwork-db.sql"
                                       "| sed 's/${password}/" + GEONETWORK_DB_PASSWORD + "/' | psql -U postgres"
                        },
                        "20-undeploy-geonetwork": {
                            "command": "rm -rf /usr/share/tomcat7/webapps/geonetwork",
                        },
                        "30-undeploy-geoscience-portal": {
                            "command": "rm -rf /usr/share/tomcat7/webapps/ROOT",
                        },
                        "35-set-geonetwork-password": {
                            "command": "(cd /usr/share/tomcat7/webapps && unzip -q geonetwork.war -d geonetwork && chown -R tomcat.tomcat geonetwork"
                                       " && sed -i 's/${password}/" + GEONETWORK_DB_PASSWORD + "/' geonetwork/WEB-INF/config-db/jdbc.properties)"
                        },
                        "40-start-tomcat": {
                            "command": "service tomcat7 start"
                        },
                    },
                )
            )
        )
    )
    with open("webserver-init.sh", "r") as user_data:
        instance.UserData = Base64(user_data.read() % {"env": environment()})

    return instance

def elb_security_group(template):
    title = "ELBSecurityGroup"
    security_group = template.add_resource(ec2.SecurityGroup(
        title,
        GroupDescription="Allow web traffic from anywhere.",
        VpcId=Ref(template.vpc.title),
        SecurityGroupIngress=[],
        Tags=Tags(
            Name=name_tag(title),
        ),
    ))
    add_http_ingress(template, security_group)
    add_https_ingress(template, security_group)
    return security_group

def webserver_security_group(vpc):
    title = "WebserverSecurityGroup"
    security_group = ec2.SecurityGroup(
        title,
        GroupDescription="Allow SSH from GA and HTTP from anywhere.",
        VpcId=Ref(vpc.title),
        SecurityGroupIngress=[],
        Tags=Tags(
            Name=name_tag(title),
        ),
    )
    return security_group

def add_ssh_ingress_from_ga(template, security_group):
    """Return an ingress for the given security group to allow
    SSH traffic from public.ga.gov.au."""
    return add_ssh_ingress(template, security_group, PUBLIC_GA_GOV_AU_PTR + '/32')

def add_ssh_ingress(template, security_group, cidr='0.0.0.0/0'):
    """Return an ingress for the given security group to allow SSH traffic."""
    return add_security_group_ingress(template, security_group, "tcp", "22", "22", cidr)

def add_http_ingress(template, security_group, cidr='0.0.0.0/0'):
    """Return an ingress for the given security group to allow HTTP traffic."""
    return add_security_group_ingress(template, security_group, "tcp", "80", "80", cidr)

def add_tomcat_ingress(template, security_group, cidr='0.0.0.0/0'):
    """Return an ingress for the given security group to allow tomcat traffic."""
    return add_security_group_ingress(template, security_group, "tcp", "8080", "8080", cidr)

def add_https_ingress(template, security_group, cidr='0.0.0.0/0'):
    """Return an ingress for the given security group to allow HTTPS traffic."""
    return add_security_group_ingress(template, security_group, "tcp", "443", "443", cidr)

def add_icmp_ingress(template, security_group, cidr='0.0.0.0/0'):
    """Return an ingress for the given security group to allow ICMP traffic."""
    return add_security_group_ingress(template, security_group, "icmp", "-1", "-1", cidr)

print(GeosciencePortalStack().to_json())
