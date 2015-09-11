# pylint: disable=missing-docstring, invalid-name, line-too-long

"""Geoscience Portal AWS CloudFormation Stack Definition
"""

import sys
from troposphere import Base64, Join, Ref, Tags, Template
from troposphere import cloudformation as cf
import troposphere.ec2 as ec2
from subprocess import call
import glob
import os
import boto

REDHAT_IMAGEID = "ami-d3daace9"
SYSTEM_PREFIX = "GeosciencePortal"
KEY_PAIR_NAME = "lazar@work"
WEBSERVER_IP = "54.206.17.34"
GA_PUBLIC_NEXUS = "http://maven-int.ga.gov.au/nexus/service/local/artifact/maven/redirect?r=public"

stack_id = Ref("AWS::StackId")
stack_name = Ref("AWS:StackName")
region = Ref("AWS::Region")

def resource_name(name):
    return SYSTEM_PREFIX + name

def stack():
    template = Template()
    security_group = template.add_resource(webserver_security_group())
    webserver = template.add_resource(make_webserver(security_group))
    assign_eip(template, webserver, WEBSERVER_IP)
    return template

def assign_eip(template, instance, ip):
    return template.add_resource(ec2.EIPAssociation(
        "WebserverIpAssociation",
        EIP=ip,
        InstanceId=Ref(instance)
    ))

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

def make_webserver(security_group):
    name = resource_name("WebServer")
    instance = ec2.Instance(
        name,
        ImageId=REDHAT_IMAGEID,
        InstanceType="t2.small",
        Tags=Tags(Name=name),
        KeyName=KEY_PAIR_NAME,
        SecurityGroups=[Ref(security_group)],
        Metadata=cf.Metadata(
            cf.Init(
                cf.InitConfigSets(
                    default=["on_create", {"ConfigSet": "update"}],
                    update=["on_update"]
                ),
                on_create=cf.InitConfig(
                    packages={
                        "yum": {
                            "telnet": [],
                            "tomcat": [],
                            "java-1.7.0-openjdk.x86_64": [],
                            "wget": [],
                            "iptables-services": [],
                            "postgresql-server": [],
                            "python-pip": [],
                            "unzip": [],
                        }
                    },
                    files=cf.InitFiles({
                        "/etc/cloud/cloud.cfg.d/99_hostname.cfg": cf.InitFile(
                            content="preserve_hostname: true",
                        ),
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
                                "path=Resources.", name, ".Metadata.AWS::CloudFormation::Init\n",
                                "action=/usr/bin/cfn-init",
                                " --stack ", stack_id,
                                " --resource ", name,
                                " --region ", region,
                                " -c update\n",
                                "runas=root\n"
                            ]),
                        ),
                        "/root/.pgpass": cf.InitFile(
                            content="localhost:5432:*:postgres:secret",
                            mode="0600",
                        ),
                        "/var/lib/pgsql/password": cf.InitFile(
                            content="secret",
                            owner="postgres",
                            mode="0600",
                        ),
                    }),
                    commands={
                        "00-redirect-port-80-to-port-8080": {
                            "command": "iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080 && iptables-save > /etc/sysconfig/iptables"
                        },
                        "10-allow-sudo-without-tty": {
                            "command": "sed -i '/Defaults    requiretty/s/^/#/g' /etc/sudoers"
                        },
                        "20-init-postgres": {
                            "command": "sudo -u postgres initdb -D /var/lib/pgsql/data -A md5 --pwfile=/var/lib/pgsql/password"
                        },
                    },
                    services={
                        "sysvinit": cf.InitServices({
                            "postgresql": cf.InitService(
                                enabled=True,
                                ensureRunning=True,
                            ),
                            "tomcat": cf.InitService(
                                enabled=True,
                                ensureRunning=True,
                            ),
                            "iptables": cf.InitService(
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
                        "/usr/share/tomcat/webapps/ROOT.war": cf.InitFile(
                            source=get_geoscience_portal_war_url(),
                            owner="tomcat",
                            group="tomcat",
                        ),
                        "/usr/share/tomcat/webapps/geonetwork.war": cf.InitFile(
                            source=get_geoscience_portal_geonetwork_war_url(),
                            owner="tomcat",
                            group="tomcat",
                        ),
                    }),
                    commands={
                        "00-setup-geonetwork-database": {
                            "command": "unzip -p /usr/share/tomcat/webapps/geonetwork.war WEB-INF/classes/geonetwork-db.sql | psql -U postgres"
                        },
                        "10-restart-tomcat": {
                            "command": "service tomcat restart"
                        },
                    },
                )
            )
        )
    )

    with open("webserver-init.sh", "r") as user_data:
        instance.UserData = Base64(user_data.read())

    return instance

def webserver_security_group():
    security_group = ec2.SecurityGroup(
        "WebserverSecurityGroup",
        GroupDescription="Allow SSH from GA and HTTP from anywhere.",
        SecurityGroupIngress=[]
    )
    allow_ssh_from_ga(security_group)
    allow_http(security_group)
    return security_group

def allow_ssh_from_ga(security_group):
    security_group.SecurityGroupIngress.append(
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp="192.104.44.129/32"
        )
    )

def allow_http(security_group):
    security_group.SecurityGroupIngress.append(
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="80",
            ToPort="80",
            CidrIp="0.0.0.0/0"
        )
    )
    security_group.SecurityGroupIngress.append(
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="8080",
            ToPort="8080",
            CidrIp="0.0.0.0/0"
        )
    )

print(stack().to_json())
