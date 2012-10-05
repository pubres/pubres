#!/usr/bin/env python

import argparse
import logging

import pubres


def make_parser():
    parser = argparse.ArgumentParser(description='pubres server.')
    parser.add_argument('--host', type=str, default='localhost', help='host to listen on (omit for localhost)')
    parser.add_argument('--port', type=int, default=5555, help='port to listen on (default is 5555)')
    parser.add_argument('--loglevel', type=str, default='INFO', help='Log level. DEBUG, INFO, WARNING, ERROR or CRITICAL.')
    return parser


def setup_logging(level):
    # Check if the log level string is one defined in logging
    numeric_level = getattr(logging, level.upper())
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % level)

    ## Logger, handler and formatter

    logger = logging.getLogger('pubres')
    logger.setLevel(numeric_level)

    handler = logging.StreamHandler()
    handler.setLevel(numeric_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def main():
    args = make_parser().parse_args()

    setup_logging(level=args.loglevel)

    pubres.Server(host=args.host, port=args.port).serve_forever()


if __name__ == '__main__':
    main()
