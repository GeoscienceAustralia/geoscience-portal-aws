#!/bin/bash
export AWS_PROFILE=geoscience-portal
PATH=~/.local/bin:$PATH
make clean restack

