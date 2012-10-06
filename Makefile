all: test

.PHONY: all test test_repeated run_coverage coverage

test:
	./tests.py

test_repeated:
	./tests.py --repeated

run_coverage:
	python-coverage run --source=. tests.py

coverage: run_coverage
	python-coverage report

coverage_html: run_coverage
	rm -rf htmlcov/
	python-coverage html
