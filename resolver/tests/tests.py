import socket
import threading
from nose.tools import *

HOST, PORT = 'localhost', 5555


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
        raise Exception('resolver did not tell it is ready')
    return s


class pub(object):
    def __init__(self, key, val):
        super(pub, self).__init__()
        self.key = key
        self.val = val
        self.keep_open_thread = None
        self.running = True

        self.sock = connect()
        self.sock.sendall('pub %s %s\n' % (self.key, self.val))
        answer = self.sock.recv(128)
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
    answer = s.recv(128)
    if 'ok' not in answer:
        raise QueryFailed(key, answer)

    data = s.recv(1024)
    s.close()
    return data.strip()


def assert_key_not_found(fn):
    try:
        fn()
    except QueryFailed as e:
        assert_equal(e.server_message, 'key not found')


def test_subscribe():
    with pub('key1', 'val1'):
        pass


def test_query():
    with pub('key1', 'val1'):
        assert_equal(query('key1'), 'val1')


def test_unsubscribe():
    with pub('key1', 'val1'):
        pass
    assert_key_not_found(lambda: query('key1'))


def test_pub_query_unsubscribe():
    with pub('key1', 'val1'):
        assert_equal(query('key1'), 'val1')
        assert_key_not_found(lambda: query('uknownkey'))

    assert_key_not_found(lambda: query('key1'))
