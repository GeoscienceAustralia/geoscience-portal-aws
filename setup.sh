#!/bin/bash
export APP_NAME=GeosciencePortal
export STACK_NAME=$APP_NAME'Dev' # $APP_NAME$ENVIRONMENT
#export JUMPBOX=$STACK_NAME'_jumpbox'
export JUMPBOX='tag_Name_'$STACK_NAME'_jumpbox'


usermod -aG staff $USER

cp ./ansible/geoscience-portal-rsa  ~/.ssh/
chmod 600 ~/.ssh/geoscience-portal-rsa

eval `ssh-agent`
ssh-add ~/.ssh/geoscience-portal-rsa