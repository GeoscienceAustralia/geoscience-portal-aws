## AWS Infrastructure for Geoscience Portal

#### Prerequisites
```
pip install awscli boto troposphere
aws configure
```

#### Usage
```
GEOSCIENCE_PORTAL_VERSION=1.0.0-SNAPSHOT GEOSCIENCE_GEONETWORK_VERSION=1.0.0-SNAPSHOT make stack
make unstack
```
