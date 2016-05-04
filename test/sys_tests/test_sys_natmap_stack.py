#!/usr/bin/python3

from amazonia.classes.stack import Stack


def main():
    userdata1 = """#cloud-config

# Capture all cloud-config output into a more readable logfile
output: {all: '| tee -a /var/log/cloud-init-output.log'}

# update and install packages, reboot if necessary
package_upgrade: true
package_reboot_if_required: true
packages:
 - ntp
 - python-pip
 - nodejs-legacy
 - npm
 - varnish
 - gdal-bin

# any files to create
write_files:

 - path: /etc/varnish/default.vcl
   content: |
    backend default {
        .host = "127.0.0.1";
        .port = "3001";
    }

    acl purge {
      "localhost";
      "127.0.0.1";
    }


    sub vcl_recv {
    #  if (req.request == "GET" && req.http.cookie || req.http.authorization) {
    #    return (lookup);
    #  }
      if (req.request == "PURGE") {
        if (!client.ip ~ purge) {
          error 405 "Method Not Allowed";
        }
        return(lookup);
      }
      if (req.url ~ "^/proxy"){
        return (lookup);
      }
    }

    sub vcl_hit {
      if (req.request == "PURGE") {
        purge;
        error 200 "Purged";
      }
    }

    sub vcl_miss {
      if (req.request == "PURGE") {
        purge;
        error 200 "Purged";
      }
    }

    sub vcl_fetch
    {
      if ( beresp.status >= 400 ) {
        set beresp.ttl = 0s;
      }
    }

 - path: /etc/default/varnish
   content: |
    START=yes
    NFILES=131072
    MEMLOCK=82000
    DAEMON_OPTS="-a :80 -T localhost:6082 -f /etc/varnish/default.vcl -S /etc/varnish/secret -s memcache=malloc,2G -s filecache=file,/tmp/varnish_storage.bin,10G"

 - path: /etc/rsyslog.d/30-natmap.conf
   content: |
    :syslogtag, isequal, "natmap:" /var/log/natmap.log
    & ~

 - path: /etc/init/natmap.conf
   content: |
    start on (net-device-up and local-filesystems and runlevel [2345])
    stop on runlevel [016]
    console log
    exec bash -c "cd /opt/natmap-2016-04-05 && /opt/natmap-2016-04-05/run_server.sh 2>&1 | logger -t natmap"

# run all the commands to set this instance up
runcmd:
 - echo 'APT::Periodic::Unattended-Upgrade "1";' >> /etc/apt/apt.conf.d/10periodic

# copy and extract the webapps from S3
 - mkdir /tmp/ramfs

# natmap
 - mount -t ramfs ramfs /tmp/ramfs
 - wget https://s3-ap-southeast-2.amazonaws.com/smallest-bucket-in-history/natmap/natmap-2016-04-05.tar.gz -O /tmp/ramfs/natmap-2016-04-05.tar.gz
 - mkdir /opt/natmap-2016-04-05
 - tar xzf /tmp/ramfs/natmap-2016-04-05.tar.gz -C /opt/natmap-2016-04-05
 - umount /tmp/ramfs

# start/restart services
 - service rsyslog restart
 - service varnish restart
 - service natmap start
"""

    nat_image_id = 'ami-162c0c75'
    jump_image_id = 'ami-05446966'
    app_image_id = 'ami-05446966'
    instance_type = 't2.nano'
    stack = Stack(
        stack_title='test',
        code_deploy_service_role='arn:aws:iam::658691668407:role/CodeDeployServiceRole',
        keypair='pipeline',
        availability_zones=['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'],
        vpc_cidr='10.0.0.0/16',
        public_cidr='0.0.0.0/0',
        jump_image_id=jump_image_id,
        jump_instance_type=instance_type,
        nat_image_id=nat_image_id,
        nat_instance_type=instance_type,
        home_cidrs=[('GA', '192.104.44.129/32')],
        units=[{'unit_title': 'app1',
                'protocols': ['HTTP'],
                'instanceports': ['80'],
                'loadbalancerports': ['80'],
                'path2ping': '/index.html',
                'minsize': 1,
                'maxsize': 1,
                'health_check_grace_period': 1200,
                'health_check_type': 'ELB',
                'image_id': app_image_id,
                'instance_type': instance_type,
                'hosted_zone_name': None,
                'iam_instance_profile_arn': None,
                'userdata': userdata1}
               ]

    )
    print(stack.template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
