#!/usr/bin/python3
import boto3
import time
import json
from amazonia.amazonia import amz

"""
This Script will take a cloud formation template file and upload it to create a cloud formation stack in aws using boto3
http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack
"""
cf_client = boto3.client('cloudformation')
s3_client = boto3.client('s3')

# TODO get amz to output to file
# template = amz.main()
#
aws_template = open('stack.template', 'rb')


s3_response = s3_client.put_object(
    Body=aws_template,
    Bucket='smallest-bucket-in-history',
    Key='smallest_app_in_history/astack.template')

print('response={0}'.format(s3_response))




# TODO match yaml to args
stack_name = args.stack
template_url = args.url
environment = args.env
app = args.app
infra_code_version = args.infra_code_version
tags = args.tags
time_delay = args.time

create_response = cf_client.create_stack(
    StackName=stack_name,
    TemplateURL=template_url,
    TimeoutInMinutes=123,
    ResourceTypes=['AWS::*'],
    OnFailure='ROLLBACK',
    Tags=[
        {
            'Key': 'Environment',
            'Value': environment
        },
        {
            'Key': 'Application',
            'Value': app
        },
        {
            'Key': 'Infra_Code_Version',
            'Value': infra_code_version
        },
        tags,

    ]
)

print('StackId:\n {0}\n'.format(create_response))


"""
Script to return an AWS Cloudformation Stack_ID or Stack_Name stack status every 10 seconds using boto3.
If the status returns CREATE_COMPLETE then exit with success message
If the status returns ROLLBACK_IN_PROGRESS or ROLLBACK_COMPLETE then exit with failure message
http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_events
"""
while stack_name:
    confirm_response = cf_client.describe_stacks(StackName=stack_name)
    stack_status = confirm_response['Stacks'][0]['StackStatus']

    if stack_status == 'CREATE_COMPLETE':
        print('Stack Successfully Created, Stack Status: {0}'.format(stack_status))
        break
    elif stack_status in ('ROLLBACK_IN_PROGRESS', 'ROLLBACK_COMPLETE'):
        print('Error occurred creating AWS CloudFormation stack and returned status code {0}.'.format(stack_status))
        break
    else:
        print('Stack Status: {0}'.format(stack_status))
    time.sleep(time_delay)

"""
This script will delete a stack in AWS
http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack
"""
delete_response = cf_client.delete_stack(StackName=stack_name)

print('Stack {0} Deletion Commencing'.format(stack_name))
