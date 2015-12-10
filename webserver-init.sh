#cloud-config

hostname: portal-dev

runcmd:
- /opt/aws/bin/cfn-init --region ap-southeast-2 -s GeosciencePortal%(env)s -r WebserverLaunchConfig
