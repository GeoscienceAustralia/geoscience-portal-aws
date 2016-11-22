#!/bin/bash
export AWS_PROFILE=geoscience-portal
PATH=~/.local/bin:$PATH
ENV=Test GEOSCIENCE_PORTAL_VERSION=1.0.0 GEOSCIENCE_GEONETWORK_VERSION=1.0.0-SNAPSHOT make clean restack
