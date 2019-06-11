#direct external HTTP traffic to the webserver in the private subnet
# local_ip=`curl http://169.254.169.254/latest/meta-data/local-ipv4`
# iptables -t nat -A PREROUTING -i eth0 -p tcp -d $local_ip --dport 80 -j DNAT --to 10.0.1.100:80 && iptables-save > /etc/sysconfig/iptables
curl -X PUT -H 'Content-Type:' --data-binary '{"Status" : "SUCCESS","Reason" : "Configuration Complete","UniqueId" : "ID1234","Data" : "NAT is ready"}' "$signal_url"

# Install Tenable
wget https://s3-ap-southeast-2.amazonaws.com/ga-agents/Tenable/NessusAgent-7.4.0-amzn.x86_64.rpm -O /tmp/NessusAgent-7.4.0-amzn.x86_64.rpm
wget https://s3-ap-southeast-2.amazonaws.com/ga-agents/Tenable/Agent_plugins.tgz -O /tmp/Agent_plugins.tgz
sudo rpm -ivh --force --nosignature /tmp/NessusAgent-7.4.0-amzn.x86_64.rpm
sudo chkconfig nessusagent on
sudo /opt/nessus_agent/sbin/nessuscli agent update --file=/tmp/Agent_plugins.tgz
sudo /opt/nessus_agent/sbin/nessuscli agent link --key=11731468f59adb10f0c4e16aed2257201d78d7496a42500aeec8415ead72edfb --name=geoscience-portal-prod --cloud --groups=geoscience-portal