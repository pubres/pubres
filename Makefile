all: test

.PHONY: all test test_repeated

test:
	nosetests

test_repeated:
	./tests.py
