PYTHON = `which python2.7`

virtualenv:
	rm -rf .env
	virtualenv --no-site-packages -p $(PYTHON) .env
	.env/bin/python setup.py develop 

test: virtualenv
	.env/bin/python .env/bin/nosetests -s tests

ci: virtualenv test

.PHONY: virtualenv ci test
