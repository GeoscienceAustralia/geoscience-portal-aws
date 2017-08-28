#!/bin/bash
export AWS_PROFILE=geoscience-portal
PATH=~/.local/bin:$PATH
ENV=Dev make clean restack

