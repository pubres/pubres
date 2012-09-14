#!/usr/bin/env python

import argparse

from resolver import Resolver


def main():
    parser = argparse.ArgumentParser(description='Resolver.')
    parser.add_argument('--host', type=str, default='localhost', help='host to listen on (omit for localhost)')
    parser.add_argument('--port', type=int, default=5555, help='port to listen on (default is 5555)')
    args = parser.parse_args()

    Resolver(host=args.host, port=args.port).serve_forever()


if __name__ == '__main__':
    main()
