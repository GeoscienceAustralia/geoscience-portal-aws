#!/bin/bash
export ANSIBLE_DIR=/etc/ansible

wget https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/ec2.py $ANSIBLE_DIR
wget https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/ec2.ini $ANSIBLE_DIR

export ANSIBLE_HOSTS=$ANSIBLE_DIR/ec2.py
export EC2_INI_PATH=$ANSIBLE_DIR/ec2.ini

#Get the JUMPBOX IP and over write the ssh config

export JUMPBOX_IP="$(python $ANSIBLE_DIR/ec2.py | python -c 'import sys, json, os ; print(json.load(sys.stdin)[os.environ["JUMPBOX"]][0])')"
echo $JUMPBOX_IP


cp ssh.config ~/.ssh/config && sed -i '/s/JUMPBOX_IP/$JUMPBOX_IP/'

# Replace remotely supplied ini file with our own
cp ec2.ini $ANSIBLE_DIR