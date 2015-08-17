#!/bin/bash
aws cloudformation update-stack \
    --stack-name GeosciencePortal2 \
    --template-body file:///`pwd`/stack.json \
