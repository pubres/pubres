#!/usr/bin/env python

import time
import nose
import sys
import multiprocessing

import pubres


def make_server_and_run_tests(test_suite_repetitions=100):
    server_process = multiprocessing.Process(target=pubres.Server().serve_forever)
    server_process.start()

    # Wait a bit for the server to start
    time.sleep(0.02)

    for _ in xrange(test_suite_repetitions):
        # Server must still be running
        assert server_process.is_alive()

        # Run the test suite
        if not nose.run():
            sys.exit(1)

    assert server_process.is_alive()

    # SIGTERM the server thread
    server_process.terminate()


def main():
    # A lot of servers with few requests
    for i in xrange(10):
        make_server_and_run_tests(i)

    # A server with many requests
    make_server_and_run_tests(50)


if __name__ == "__main__":
    main()
