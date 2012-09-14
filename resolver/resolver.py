import re
from gevent.server import StreamServer


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

        fp = socket.makefile()

        fp.write("resolver ready\n")
        fp.flush()

        line = fp.readline().strip()

        action, param_str = split_one_word_strip(line)

        {
            'pub': lambda: self.client_pub(fp, socket, param_str),
            'query': lambda: self.client_query(fp, socket, param_str),
            'list': lambda: self.client_list(fp, socket, param_str),
        }[action]()

    def client_pub(self, fp, socket, param_str):
        ensure_client(fp, ' ' in  param_str, "malfomred '[key] [value]'")

        key, val = split_one_word_strip(param_str)

        ensure_client(fp, is_key(key), 'invalid key')
        ensure_client(fp, is_value(val), 'invalid value')

        self.pub(key, val)

        try:
            fp.read(1)
            socket.close()
        finally:
            # Unsubscribe whatever happens and then throw the exception
            self.unpub(key)

    def client_query(self, fp, socket, param_str):
        key = param_str.strip()

        ensure_client(fp, is_key(key), 'invalid key')

        val = self.query(key)

        ensure_client(fp, val is not None, 'key not found')

        fp.write(key + '\n')
        socket.close()

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


def split_one_word_strip(line):
    return map(str.strip, line.split(' ', 1))


def ensure_client(fp, proposition, e):
    if not proposition:
        ex, msg = mk_exception_and_msg(e)
        fp.write("%s\n" % msg)
        fp.flush()
        raise ex


# Exceptions

class ResolverClientException(Exception):
    pass

class ()


KEY_RE = re.compile(r'\w+(\.\w+)*')  # At xx, xx.ab and so on


def is_key(key):
    return KEY_RE.match(key) is not None


def is_value(value):
    return True


def mk_exception_and_msg(e):
    if type(e) is str:
        return (Exception(e), e)
    else:
        return (e, e.message)
