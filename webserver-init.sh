#cloud-config

hostname: portal-dev

runcmd:
- /opt/aws/bin/cfn-init --region ap-southeast-2 -s GeosciencePortal%(env)s -r WebserverLaunchConfig

# Install Tenable
wget https://s3-ap-southeast-2.amazonaws.com/ga-agents/Tenable/NessusAgent-7.4.0-amzn.x86_64.rpm -O /tmp/NessusAgent-7.4.0-amzn.x86_64.rpm
wget https://s3-ap-southeast-2.amazonaws.com/ga-agents/Tenable/Agent_plugins.tgz -O /tmp/Agent_plugins.tgz
sudo rpm -ivh --force --nosignature /tmp/NessusAgent-7.4.0-amzn.x86_64.rpm
sudo chkconfig nessusagent on
sudo /opt/nessus_agent/sbin/nessuscli agent update --file=/tmp/Agent_plugins.tgz
sudo /opt/nessus_agent/sbin/nessuscli agent link --key=11731468f59adb10f0c4e16aed2257201d78d7496a42500aeec8415ead72edfb --name=geoscience-portal-prod --cloud --groups=geoscience-portal