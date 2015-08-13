#!/bin/bash
aws cloudformation create-stack --stack-name GeosciencePortal --template-body file:///`pwd`/stack.json
