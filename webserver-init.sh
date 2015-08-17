#!/bin/bash
set -x
echo "portal-dev" > /etc/hostname
easy_install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz
cfn-init --region ap-southeast-2 -s GeosciencePortal2 -r GeosciencePortal2WebServer
# yum -y install tomcat telnet wget
