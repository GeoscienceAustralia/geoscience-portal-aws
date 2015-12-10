stack.json: stack.py webserver-init.sh nat-init.sh
	python stack.py ${GEOSCIENCE_PORTAL_VERSION} ${GEOSCIENCE_GEONETWORK_VERSION} > $@

%.jpg: %.json
	cat $< | cfviz | dot -Tjpg -o$@

.PHONEY:
stack: stack.json
	AWS_PROFILE=geoscience-portal aws cloudformation create-stack --stack-name GeosciencePortal2 --template-body file://stack.json

.PHONEY:
restack: stack.json
	AWS_PROFILE=geoscience-portal aws cloudformation update-stack --stack-name GeosciencePortal2 --template-body file://stack.json

.PHONEY:
unstack:
	AWS_PROFILE=geoscience-portal aws cloudformation delete-stack --stack-name GeosciencePortal2

.PHONEY:
viz: stack.jpg
	xv stack.jpg

.PHONEY:
clean:
	rm -f stack.json stack.jpg *.war
