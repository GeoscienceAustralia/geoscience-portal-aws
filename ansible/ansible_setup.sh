#!/bin/bash

export ANSIBLE_DIR = /etc/ansible

mkdir $ANSIBLE_DIR

wget https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/ec2.py $ANSIBLE_DIR
cp ec2.ini $ANSIBLE_DIR

export ANSIBLE_HOSTS=$ANSIBLE_DIR/ec2.py
export EC2_INI_PATH=$ANSIBLE_DIR/ec2.ini