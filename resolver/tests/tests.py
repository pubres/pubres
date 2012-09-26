import sys
import socket
import threading

HOST, PORT = 'localhost', 5555

# TODO use testing framework instead of asserts, e.g. nose


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


def test_pub_query_1():

    # subscribe key
    with pub('key1', 'val1'):

        # key should be there
        assert query('key1') == 'val1'

        # other key should not be there
        try:
            query('uknownkey')
        except QueryFailed as e:
            assert e.server_message == 'key not found'

    # key should be gone
    try:
        query('key1')
    except QueryFailed as e:
        assert e.server_message == 'key not found'


def main():
    test_pub_query_1()
    print "all tests passed"


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print
        sys.exit(1)
