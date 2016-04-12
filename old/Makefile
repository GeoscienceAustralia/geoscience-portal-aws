#
# This makefile installs the amazonia package and its dependencies
#
# 1. to install Amazonia run "make install"
# 2. to run one of the examples run "make xxx.json" where xxx is the name of the example
# 3. to make your own automated scripts, copy one of the examples and extend it using Amazonia helper functions and the troposhpere library
# Have fun!

AutoscalingWebEnv.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/AutoscalingWebEnv > $@

dualAZ.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/dualAZ > $@

dualAZwebenv.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/dualAZwebenv > $@

ExtensionExample.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/dualAZwebenv > $@

singleAZ.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/singleAZ > $@

singleAZ_with_autoscaling_web_instance.json: amazonia/__init__.py amazonia/cftemplates.py
	python ./examples/singleAZ_with_autoscaling_web_instance > $@

.PHONEY:
build:
	python setup.py build

.PHONEY:
install:
	pip install -e . --user

.PHONEY:
uninstall:
	yes | pip uninstall amazonia

.PHONEY:
clean:
	rm -rf *.dot *.svg *.json build dist *.egg-info
