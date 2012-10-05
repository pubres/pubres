import socket
import threading
from nose.tools import assert_equal

HOST, PORT = 'localhost', 5555


# General notes:
# - We use socket.makefile().readline() instead of socket.recv()
#   because recv() doesn't guarantee to actually read all data in
#   the first call.


class ServerException(Exception):
    """An exception signalling that the server said something went wrong.
    """
    pass


class ServerExceptionWithMessage(ServerException):
    def __init__(self, server_message, details="(no details)"):
        self.server_message = server_message.strip()
        self.details = details
        msg = "%s: %s" % (self.server_message, details)
        super(ServerExceptionWithMessage, self).__init__(msg)


class PubFailed(ServerExceptionWithMessage):
    def __init__(self, key, val, msg):
        super(PubFailed, self).__init__(msg, str({key: val}))


class QueryFailed(ServerExceptionWithMessage):
    def __init__(self, key, msg):
        super(QueryFailed, self).__init__(msg, key)


def connect(host=HOST, port=PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    greeting = s.recv(128)
    if 'ready' not in greeting:
        raise Exception('pubres server did not say it is ready')
    return s


class pub(object):
    def __init__(self, key, val):
        super(pub, self).__init__()
        self.key = key
        self.val = val
        self.keep_open_thread = None
        self.running = True

        self.sock = connect()
        self.fp = self.sock.makefile()
        self.sock.sendall('pub %s %s\n' % (self.key, self.val))
        answer = self.fp.readline(128)
        if 'ok' not in answer:
            raise PubFailed(key, val, answer)

        self.keep_open_thread = threading.Thread(target=self.keep_open)
        self.keep_open_thread.start()

    def keep_open(self):
        self.sock.settimeout(0.001)  # TODO const
        while self.running:
            try:
                self.sock.recv(1)
            except socket.timeout:
                pass
        self.sock.close()

    def unpub(self):
        self.running = False
        self.keep_open_thread.join()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        self.unpub()


def query(key):
    s = connect()
    s.sendall('query %s\n' % key)
    fp = s.makefile()
    answer = fp.readline(128)
    if 'ok' not in answer:
        raise QueryFailed(key, answer)

    data = fp.readline(1024)
    s.close()
    return data.strip()


def list_str():
    s = connect()
    s.sendall('list\n')
    fp = s.makefile()
    answer = fp.readline(128)
    if 'ok' not in answer:
        raise QueryFailed(key, answer)

    data = fp.readline(4096)  # TODO tune
    s.close()
    return data.strip()


# TODO this is not a good function name in Python
def list():
    return map(str.strip, list_str().split())


def assert_key_val(key, val):
    assert_equal(query(key), val)


def assert_key_not_found(fn):
    try:
        fn()
    except QueryFailed as e:
        assert_equal(e.server_message, 'key not found')


def assert_list(expected_keys_set):
    assert_equal(list(), sorted(expected_keys_set))
