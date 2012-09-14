import re
from gevent.server import StreamServer

import exceptions


class Client(object):
    def __init__(self, socket):
        self.socket = socket
        self.fp = socket.makefile()

    def send(self, s):
        self.fp.write(s)
        self.fp.flush()

    def send_line(self, s):
        self.send(s + '\n')

    def readline(self):
        return self.fp.readline()

    def fail(self, ex):
        self.send_line(ex.message)
        print self.socket.getpeername()
        raise ex

    def ensure(self, proposition, ex):
        if not proposition:
            self.fail(ex)

    def block_and_disconnect(self):
        # TODO doc exception
        self.fp.read(1)
        self.socket.close()

    def disconnect(self):
        self.socket.close()


class Resolver(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.mapping = {}

    def serve_forever(self):
        server = StreamServer((self.host, self.port), self.handle)
        server.serve_forever()

    def handle(self, socket, address):
        print "connection from %s:%s" % (socket, address)

        client = Client(socket)

        client.send_line("resolver ready")

        line = client.readline().strip()

        action, param_str = first_word_and_rest(line)

        invalid_action_fn = lambda: client.fail(exceptions.InvalidAction())

        {
            'pub': lambda: self.client_pub(client, param_str),
            'query': lambda: self.client_query(client, param_str),
            'list': lambda: self.client_list(client, param_str),
        }.get(action, invalid_action_fn)()

    def client_pub(self, client, param_str):
        client.ensure(' ' in  param_str, exceptions.MalformedPub())

        key, val = first_word_and_rest(param_str)

        client.ensure(is_key(key), exceptions.InvalidKey())
        client.ensure(is_value(val), exceptions.InvalidValue())

        self.pub(key, val)

        # The client is now connected. We keep the connection open
        # until it disconnects (or sends something).
        try:
            client.block_and_disconnect()
        finally:
            # Unsubscribe whatever happens and then re-raise the exception
            self.unpub(key)

    def client_query(self, client, param_str):
        key = param_str.strip()

        client.ensure(is_key(key), exceptions.InvalidKey())

        val = self.query(key)

        client.ensure(val is not None, exceptions.KeyNotFound())

        client.send_line(val)

        client.disconnect()

    def client_list(self, fp, socket, param_str):
        raise Exception('not implemented')

    def pub(self, key, val):
        print "pub %s" % {key: val}
        self.mapping[key] = val

    def unpub(self, key):
        print "unpub %s" % key
        del self.mapping[key]

    def query(self, key):
        return self.mapping.get(key)


def first_word_and_rest(line):
    # str.split always returns at least one element:
    # ''.split(' ', 1) == ['']
    split = map(str.strip, line.split(' ', 1))
    return split if len(split) > 1 else split + ['']


KEY_RE = re.compile(r'\w+(\.\w+)*')  # At xx, xx.ab and so on


def is_key(key):
    return KEY_RE.match(key) is not None


def is_value(value):
    return True
