import argparse


def make_parser():
    parser = argparse.ArgumentParser(description='pubres server.')
    parser.add_argument('--host', type=str, default='localhost', help='host to listen on (omit for localhost)')
    parser.add_argument('--port', type=int, default=5555, help='port to listen on (default is 5555)')
    parser.add_argument('--loglevel', type=str, default='INFO', help='Log level. DEBUG, INFO, WARNING, ERROR or CRITICAL.')
    return parser
