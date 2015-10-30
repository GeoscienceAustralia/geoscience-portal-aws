default_vpc.json: amazonia/__init__.py amazonia/default_vpc.py
	./scripts/viz > $@

%.svg: %.json
	cat $< | cfviz | dot -Tsvg -o$@

.PHONEY:
viz: default_vpc.svg
	feh --magick-timeout 1 $<

.PHONEY:
clean:
	rm -f *.dot *.svg *.json
