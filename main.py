#!/usr/bin/env python

import argparse

import pubres


def make_parser():
    parser = argparse.ArgumentParser(description='pubres server.')
    parser.add_argument('--host', type=str, default='localhost', help='host to listen on (omit for localhost)')
    parser.add_argument('--port', type=int, default=5555, help='port to listen on (default is 5555)')
    return parser


def main():
    args = make_parser().parse_args()

    pubres.Server(host=args.host, port=args.port).serve_forever()


if __name__ == '__main__':
    main()
