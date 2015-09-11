#!/bin/bash
export AWS_PROFILE=dev-account
PATH=~/.local/bin:$PATH
make clean restack
