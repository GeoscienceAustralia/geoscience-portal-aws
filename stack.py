# pylint: disable=missing-docstring, invalid-name

"""Geoscience Portal AWS CloudFormation Stack Definition
"""

from troposphere import Base64, Ref, Tags, Template
from troposphere import cloudformation as cf
import troposphere.ec2 as ec2

REDHAT_IMAGEID = "ami-d3daace9"
SYSTEM_PREFIX = "GeosciencePortal2"
KEY_PAIR_NAME = "lazar@work"
WEBSERVER_IP = "54.153.211.253"

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
                            "wget": [],
                        }
                    },
                    files={
                        "/usr/share/tomcat/webapps/geonetwork.war": {
                            "source": "http://internode.dl.sourceforge.net/project/geonetwork/GeoNetwork_opensource/v3.0.1/geonetwork.war",
                            "owner": "tomcat",
                            "group": "tomcat",
                        },
                    },
                    services={
                        "sysvinit": {
                            "tomcat": {
                                "enabled": "true",
                                "ensureRunning": "true",
                            }
                        }
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
        GroupDescription="Allow SSH and HTTP from anywhere.",
        SecurityGroupIngress=[]
    )
    allow_ssh(security_group)
    allow_http(security_group)
    return security_group

def allow_ssh(security_group):
    security_group.SecurityGroupIngress.append(
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp="0.0.0.0/0"
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
