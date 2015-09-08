stack.json: stack.py webserver-init.sh
	python2 stack.py 1.0.0-SNAPSHOT 1.0.0-SNAPSHOT > $@

.PHONEY:
stack: stack.json 
	aws cloudformation create-stack --stack-name GeosciencePortal --template-body file:///`pwd`/stack.json

.PHONEY:
restack: stack.json
	aws cloudformation update-stack --stack-name GeosciencePortal --template-body file:///`pwd`/stack.json

.PHONEY:
unstack: 
	aws cloudformation delete-stack --stack-name GeosciencePortal

.PHONEY:
clean:
	rm -f stack.json *.war
