.PHONEY:
build:
	python setup.py build


cftemplate.json: amazonia/__init__.py amazonia/default_vpc.py
	./scripts/viz > $@


default_vpc.json: amazonia/__init__.py amazonia/default_vpc.py
	./scripts/viz > $@

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
