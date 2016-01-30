#
# This makefile installs the amazonia package and its dependencies
#
# 1. to install Amazonia run "make install" 
# 2. to run one of the examples run "make xxx.json" where xxx is the name of the example
# 3. to make your own automated scripts, copy one of the examples and extend it using Amazonia helper functions and the troposhpere library
# Have fun!


.PHONEY:
build:
	python setup.py build


simpleEnv.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/simpleEnv > $@

singleAZ.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/singleAZ > $@

dualAZ.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/dualAZ > $@

dualAZwebenv.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/dualAZwebenv > $@

singleAZScalingWeb.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/singleAZ_with_autoscaling_web_instance > $@

default_vpc.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/viz > $@

%.svg: %.json
	cat $< | cfviz | dot -Tsvg -o$@

.PHONEY:
viz: default_vpc.svg
	feh --magick-timeout 1 $< &

.PHONEY:
install:
	pip install -e . --user

.PHONEY:
uninstall:
	yes | pip uninstall amazonia

.PHONEY:
clean:
	rm -rf *.dot *.svg *.json build dist *.egg-info
