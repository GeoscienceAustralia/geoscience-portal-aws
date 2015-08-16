#!/bin/bash
set -x
echo "portal-dev" > /etc/hostname
yum -y install tomcat telnet wget
(cd /usr/share/tomcat/webapps; wget http://internode.dl.sourceforge.net/project/geonetwork/GeoNetwork_opensource/v3.0.1/geonetwork.war; chown tomcat.tomcat geonetwork.war)
systemctl enable tomcat
systemctl start tomcat
