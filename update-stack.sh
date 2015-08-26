#!/bin/bash
aws cloudformation update-stack \
    --stack-name GeosciencePortal \
    --template-body file:///`pwd`/stack.json \
