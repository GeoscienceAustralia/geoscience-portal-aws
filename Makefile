stack.json: stack.py webserver-init.sh
	python2 stack.py 1.0.0-SNAPSHOT > $@

.PHONEY:
stack: stack.json 
	./create-stack.sh

.PHONEY:
unstack: 
	./delete-stack.sh

.PHONEY:
clean:
	rm stack.json
