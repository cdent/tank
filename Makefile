# Simple Makefile for some common tasks. This will get
# fleshed out with time to make things easier on developer
# and tester types.
.PHONY: test dist release pypi clean

test:
	py.test -x --tb=short test

dist: test
	python setup.py sdist

release: clean pypi

pypi: test
	python setup.py sdist upload

clean:
	find . -name "*.pyc" | xargs rm || true
	rm -r dist || true
	rm -r store || true
	rm -r build || true
	rm tiddlyweb.log || true
	rm -r *.egg-info || true
