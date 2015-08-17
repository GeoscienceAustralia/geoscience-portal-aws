#!/bin/bash
aws cloudformation create-stack \
    --stack-name GeosciencePortal2 \
    --template-body file:///`pwd`/stack.json \
