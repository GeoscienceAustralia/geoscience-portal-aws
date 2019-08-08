stack.json: stack.py webserver-init.sh nat-init.sh #war-file
	python3 stack.py ${GEOSCIENCE_PORTAL_VERSION} ${GEOSCIENCE_GEONETWORK_VERSION} ${ENV} > $@

%.jpg: %.json
	cat $< | cfviz | dot -Tjpg -o$@

war-file:
		mvn package -Dmaven.wagon.http.ssl.insecure=true -Dmaven.wagon.http.ssl.allowall=true -Dmaven.test.skip=true

.PHONEY:
stack: stack.json
	AWS_PROFILE=geoscience-portal aws cloudformation create-stack --stack-name GeosciencePortal${ENV} --template-body file://stack.json

.PHONEY:
restack: stack.json
	AWS_PROFILE=geoscience-portal aws cloudformation update-stack --stack-name GeosciencePortal${ENV} --template-body file://stack.json

.PHONEY:
unstack:
	AWS_PROFILE=geoscience-portal aws cloudformation delete-stack --stack-name GeosciencePortal${ENV}

.PHONEY:
viz: stack.jpg
	xv stack.jpg

.PHONEY:
clean:
	rm -rf stack.json stack.jpg 
