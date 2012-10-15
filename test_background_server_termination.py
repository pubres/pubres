#!/usr/bin/env python

# A quick check to see if the BackgroundServer terminates.
# Should simply exit without error after 1 second.

import time

import pubres


def main():
    server = pubres.BackgroundServer()
    server.start()

    time.sleep(1)

    server.stop()


if __name__ == '__main__':
    main()
