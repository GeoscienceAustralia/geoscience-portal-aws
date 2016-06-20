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


####Subtree commands
```
git clone git@github.com:GeoscienceAustralia/geoscience-portal-aws.git
cd geoscience-portal-aws/
git remote add -f amazonia git@github.com:GeoscienceAustralia/private_amazonia.git
git merge -s ours --no-commit amazonia/master
git read-tree --prefix=amazonia -u 589ba956ab4eb352746fb076b7b5d77566983c4a
git add amazonia
git commit -m "Add amazonia subtree"
git push
```
