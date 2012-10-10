all: test

.PHONY: all test test_repeated run_coverage coverage

test:
	# Run only fast tests
	py.test -k-slow

test_repeated:
	# Run all tests
	py.test

coverage:
	# Requires pytest-cov
	py.test -k-slow --cov pubres

coverage_html: run_coverage
	# Requires pytest-cov
	py.test -k-slow --cov pubres --cov-report html
