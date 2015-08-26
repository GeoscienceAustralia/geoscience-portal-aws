# pylint: disable=missing-docstring, invalid-name, line-too-long

"""Geoscience Portal AWS CloudFormation Stack Definition
"""

import sys
from troposphere import Base64, Join, Ref, Tags, Template
from troposphere import cloudformation as cf
import troposphere.ec2 as ec2
# import troposphere.iam as iam
from subprocess import call
import glob
import os
import boto

REDHAT_IMAGEID = "ami-d3daace9"
SYSTEM_PREFIX = "GeosciencePortal2"
KEY_PAIR_NAME = "lazar@work"
WEBSERVER_IP = "54.153.211.253"
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
    # webserver_instance_profile = template.add_resource(iam.InstanceProfile(
    #     "InstanceProfile",
    #     Path="/",
    #     Roles=["DeveloperAdmin"],
    # ))
    # webserver.IamInstanceProfile = Ref(webserver_instance_profile)
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

def get_geoscience_portal_war_url():
    arg = GA_PUBLIC_NEXUS + '&g=au.gov.ga&a=geoscience-portal&v=' + geoscience_portal_version() + '&e=war'
    call(["wget", arg, '--content-disposition', "--timestamping"])
    war_filename = max(glob.iglob("*.war"), key=os.path.getctime)
    call(["aws", "s3", "cp", war_filename, "s3://ga-gov-au/mvn-snapshot/", "--quiet", "--acl", "public-read"])
    s3 = boto.connect_s3()
    bucket = s3.get_bucket("ga-gov-au")
    key = bucket.get_key("mvn-snapshot/" + war_filename)
    return key.generate_url(3600)
    # return "http://s3-ap-southeast-2.amazonaws.com/ga.gov.au/mvn-snapshot/" + war_filename

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
                    default=["config"]
                ),
                config=cf.InitConfig(
                    packages={
                        "yum": {
                            "telnet": [],
                            "tomcat": [],
                            "java-1.7.0-openjdk.x86_64": [],
                            "wget": [],
                        }
                    },
                    files=cf.InitFiles({
                        "/usr/share/tomcat/webapps/geonetwork.war": cf.InitFile(
                            source="http://internode.dl.sourceforge.net/project/geonetwork/GeoNetwork_opensource/v3.0.1/geonetwork.war",
                            owner="tomcat",
                            group="tomcat",
                        ),
                        "/usr/share/tomcat/webapps/geoscience-portal.war": cf.InitFile(
                            source=get_geoscience_portal_war_url(),
                            owner="tomcat",
                            group="tomcat",
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
                                " --region ", region, "\n",
                                "runas=root\n"
                            ]),
                        ),
                    }),
                    services={
                        "sysvinit": cf.InitServices({
                            "tomcat": cf.InitService(
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
                    }
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
