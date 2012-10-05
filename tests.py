#!/usr/bin/env python

import sys
import nose

REPETITIONS = 100


def main():
    for x in xrange(REPETITIONS):
        if not nose.run():
            sys.exit(1)


if __name__ == "__main__":
    main()
