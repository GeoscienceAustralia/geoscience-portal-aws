stack.json: stack.py webserver-init.sh nat-init.sh
	python2 stack.py 1.0.0-SNAPSHOT 1.0.0-SNAPSHOT > $@

%.svg: %.json
	cat $< | cfviz | dot -Tsvg -o$@

.PHONEY:
stack: stack.json 
	aws cloudformation create-stack --stack-name GeosciencePortal2 --template-body file://stack.json

.PHONEY:
restack: stack.json
	aws cloudformation update-stack --stack-name GeosciencePortal2 --template-body file://stack.json

.PHONEY:
unstack: 
	aws cloudformation delete-stack --stack-name GeosciencePortal2

.PHONEY:
viz: stack.svg
	feh --magick-timeout 1 stack.svg

.PHONEY:
clean:
	rm -f stack.json stack.svg *.war
