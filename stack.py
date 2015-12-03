# pylint: disable=missing-docstring, invalid-name, line-too-long

"""Geoscience Portal AWS CloudFormation Stack Definition
"""

import glob
import os
import random
import string
from   subprocess import call
import sys

import boto

from   troposphere import Base64, Join, Ref, Tags, Template
from   troposphere import cloudformation as cf
import troposphere.ec2 as ec2

from   amazonia import http_ingress, icmp_ingress, ssh_ingress, name_tag
import amazonia.default_vpc as default_vpc

IMAGE_ID = "ami-48d38c2b"
SYSTEM_PREFIX = "GeosciencePortal"
KEY_PAIR_NAME = "lazar@work"
NAT_IP = "54.206.17.34"
GA_PUBLIC_NEXUS = "http://maven-int.ga.gov.au/nexus/service/local/artifact/maven/redirect?r=public"

def _generate_password():
    return ''.join(random.sample(string.ascii_letters + string.digits, 10))

POSTGRES_SUPERUSER_PASSWORD = _generate_password()
GEONETWORK_DB_PASSWORD = _generate_password()

stack_id = Ref("AWS::StackId")
stack_name = Ref("AWS:StackName")
region = Ref("AWS::Region")

def stack():
    template = Template()
    vpc = default_vpc.add_vpc(template, KEY_PAIR_NAME, NAT_IP)
    nat = default_vpc.nat_instance(template)
    security_group = template.add_resource(webserver_security_group(vpc))
    template.add_resource(http_ingress(security_group))
    template.add_resource(icmp_ingress(security_group))
    template.add_resource(ssh_ingress(security_group))

    nat_wait_handle = template.add_resource(cf.WaitConditionHandle("natWaitHandle"))
    wait_title = "WaitFor" + nat.title
    nat_wait = template.add_resource(cf.WaitCondition(
        wait_title,
        Handle=Ref(nat_wait_handle),
        DependsOn=nat.title,
        Timeout="1200",
    ))

    webserver = make_webserver(nat_wait, default_vpc.private_subnet(template), security_group)
    template.add_resource(webserver)

    with open("nat-init.sh", "r") as user_data:
        nat.UserData = Base64(Join("", ["#!/bin/bash\n", "signal_url='", Ref(nat_wait_handle), "'\n", user_data.read()]))

    return template


def geoscience_portal_version():
    return sys.argv[1]

def geoscience_portal_geonetwork_version():
    return sys.argv[2]

def get_nexus_artifact_url(group_id, artifact_id, version):
    arg = GA_PUBLIC_NEXUS + '&g=' + group_id + '&a=' + artifact_id + '&v=' + version + '&e=war'
    call(["wget", arg, '--content-disposition', "--timestamping"])
    war_filename = max(glob.iglob(artifact_id + "*.war"), key=os.path.getctime)
    call(["aws", "s3", "cp", war_filename, "s3://ga-gov-au/mvn-snapshot/", "--quiet", "--acl", "public-read"])
    call(["rm", war_filename])
    s3 = boto.connect_s3()
    bucket = s3.get_bucket("ga-gov-au")
    key = bucket.get_key("mvn-snapshot/" + war_filename)
    return key.generate_url(3600)

def get_geoscience_portal_war_url():
    return get_nexus_artifact_url("au.gov.ga", "geoscience-portal", geoscience_portal_version())

def get_geoscience_portal_geonetwork_war_url():
    return get_nexus_artifact_url("au.gov.ga", "geoscience-portal-geonetwork", geoscience_portal_geonetwork_version())

def make_webserver(nat_wait, subnet, security_group):
    instance_id = "Webserver"
    instance = ec2.Instance(
        instance_id,
        ImageId=IMAGE_ID,
        InstanceType="t2.medium",
        Tags=Tags(Name=name_tag(instance_id)),
        KeyName=KEY_PAIR_NAME,
        SubnetId=Ref(subnet.title),
        SecurityGroupIds=[Ref(security_group.title)],
        PrivateIpAddress="10.0.1.100",
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
                            "python34": [],
                            "postgresql92-server": [],
                            "unzip": [],
                        }
                    },
                    files=cf.InitFiles({
                        "/etc/cfn/cfn-hup.conf": cf.InitFile(
                            content=Join('', [
                                "[main]\n",
                                "stack=", stack_id, "\n",
                                "region=", region, "\n",
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
                        "10-redirect-port-80-to-port-8080": {
                            "command": "iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080 && iptables-save > /etc/sysconfig/iptables"
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
        instance.UserData = Base64(user_data.read())

    return instance

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

print(stack().to_json())
