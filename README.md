## AWS Infrastructure for Geoscience Portal

#### Prerequisites
`pip install awscli boto troposhpere`

`aws configure`

#### Usage
`GEOSCIENCE_PORTAL_VERSION=1.0.0-SNAPSHOT GEOSCIENCE_GEONETWORK_VERSION=1.0.0-SNAPSHOT make stack`

`GEOSCIENCE_PORTAL_VERSION=1.0.0-SNAPSHOT GEOSCIENCE_GEONETWORK_VERSION=1.0.0-SNAPSHOT make restack`

`make unstack`
