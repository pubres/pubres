#!/usr/bin/env python

import argparse
import time
import pytest
import sys
import logging
import multiprocessing

import pubres


def make_server_and_run_tests(test_suite_repetitions=100, nose_args=[]):

    # Start server
    server_process = multiprocessing.Process(target=pubres.Server().serve_forever)
    server_process.start()
    # Wait a bit for the server to start
    time.sleep(0.02)

    nose_argv = sys.argv[:1] + nose_args

    for _ in xrange(test_suite_repetitions):
        # Server must still be running
        assert server_process.is_alive()

        # Run the test suite
        if pytest.main():
            sys.exit(1)

    assert server_process.is_alive()

    # SIGTERM the server thread
    server_process.terminate()


def run_repeated_tests(nose_args=[]):
    # A lot of servers with few requests
    for i in xrange(10):
        make_server_and_run_tests(i, nose_args=nose_args)

    # A server with many requests
    make_server_and_run_tests(50, nose_args=nose_args)


def main():
    # Turn logging off
    logging.getLogger('pubres').addHandler(logging.NullHandler())

    parser = argparse.ArgumentParser(description='pubres tests.')
    parser.add_argument('--repeated', action='store_true', help='run tests many times')

    (args, nose_args) = parser.parse_known_args()

    if args.repeated:
        run_repeated_tests(nose_args=nose_args)
    else:
        # Just one test run
        make_server_and_run_tests(1, nose_args=nose_args)


if __name__ == "__main__":
    main()
