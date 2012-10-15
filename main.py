#!/usr/bin/env python

import argparse
import logging

import pubres
from pubres.pubres_logging import setup_logging
from pubres.cli_arguments import make_parser


def main():
    args = make_parser().parse_args()

    setup_logging(level=args.loglevel)

    pubres.Server(host=args.host, port=args.port).run_until_stop()


if __name__ == '__main__':
    main()
