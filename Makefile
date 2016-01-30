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
