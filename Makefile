all: test

.PHONY: all test test_repeated coverage

test:
	nosetests

test_repeated:
	./tests.py

coverage:
	nosetests --with-coverage --cover-package=pubres

coverage_html:
	rm -rf cover/
	nosetests --with-coverage --cover-html --cover-package=pubres
