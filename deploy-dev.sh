#!/bin/bash
export AWS_PROFILE=geoscience-portal
export GEOSCIENCE_PORTAL_VERSION=1.4.2-SNAPSHOT
export GEOSCIENCE_GEONETWORK_VERSION=1.0.0-SNAPSHOT 
PATH=~/.local/bin:$PATH
ENV=Dev make restack
