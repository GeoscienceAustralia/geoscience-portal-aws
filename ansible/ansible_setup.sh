#!/bin/bash

$ANSIBLE_DIR = /etc/ansible

mkdir $ANSIBLE_DIR

wget https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/ec2.py $ANSIBLE_DIR
cp ec2.ini $ANSIBLE_DIR