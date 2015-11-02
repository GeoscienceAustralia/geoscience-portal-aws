#cloud-config

hostname: portal-dev

runcmd:
 - hostnamectl --static set-hostname portal-dev.geoscience.gov.au
 - rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
 - easy_install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz
 - ln -s /usr/lib/python2.7/site-packages/aws_cfn_bootstrap-1.4-py2.7.egg/init/redhat/cfn-hup /etc/init.d/cfn-hup
 - chmod 755 /usr/lib/python2.7/site-packages/aws_cfn_bootstrap-1.4-py2.7.egg/init/redhat/cfn-hup
 - mkdir -p /opt/aws/bin
 - ln -s /usr/bin/cfn-hup /opt/aws/bin/cfn-hup
 - cfn-init --region ap-southeast-2 -s GeosciencePortal -r Webserver
