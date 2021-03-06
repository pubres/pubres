import logging
import multiprocessing
import re
import gevent
import gevent.server
import gevent.event

import exceptions

__all__ = [
    'Server',
    'BackgroundServer',
]

logger = logging.getLogger('pubres')


class Client(object):
    def __init__(self, socket):
        self._socket = socket
        self._fp = socket.makefile()
        # Docs claim socket.getpeername() does not work on all platforms.
        self.peername = socket.getpeername()

    def send(self, s):
        self._fp.write(s)
        self._fp.flush()

    def send_line(self, s):
        self.send(s + '\n')

    def readline(self):
        return self._fp.readline()  # TODO length limit

    def fail(self, ex):
        self.send_line(ex.message)
        raise ex

    def ensure(self, proposition, ex):
        if not proposition:
            self.fail(ex)

    def block_and_disconnect(self):
        # TODO doc exception
        self._fp.read(1)
        self._socket.close()

    def disconnect(self):
        self._socket.close()


class CallbackStreamServer(gevent.server.StreamServer):
    """A StreamServer that calls a callback when it finished starting
    so that code that starts it using serve_forever doesn't have to
    wait some arbitrary time for the socket to get bound.
    """
    def __init__(self, *args, **kwargs):
        # Extract the started_callback and don't pass it to the StreamServer constructor
        other_kwargs = kwargs.copy()
        self._started_callback = other_kwargs.pop('started_callback', None)
        super(CallbackStreamServer, self).__init__(*args, **other_kwargs)

    def pre_start(self, *args, **kwargs):
        # See http://www.gevent.org/gevent.baseserver.html#gevent.baseserver.BaseServer.pre_start
        super(CallbackStreamServer, self).pre_start(*args, **kwargs)

        if self._started_callback:
            self._started_callback()


class Server(object):

    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.mapping = {}
        self._mp_server_stop_event = multiprocessing.Event()

    def run_until_stop(self, started_callback=None, poll_time=0.001):
        """Starts the server.
        Blocks until stop() is called (possibly from another process).

        Does a gevent.sleep(1ms) loop as actually wait()ing for a
        multiprocessing.Event would block all gevent activity,
        so we have to poll.

        This sleeping time can be overridden with the poll_time parameter
        (in seconds).
        """
        gevent_server = CallbackStreamServer((self.host, self.port), self.on_connection, started_callback=started_callback)
        gevent_server.start()

        while not self._mp_server_stop_event.is_set():
            gevent.sleep(poll_time)

        gevent_server.stop()

    def stop(self):
        """Stops the server. Does not block.
        """
        self._mp_server_stop_event.set()

    def on_connection(self, socket, address):
        logger.debug("connection from %s", address)

        client = Client(socket)
        try:
            client.send_line("pubres ready")
            self.handle_client(client)
        except exceptions.ClientException as e:
            logger.warning("%s - %s", client.peername, e.message)

    def handle_client(self, client):
        # TODO timeout
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

        ok = self.pub(key, val)

        if not ok:
            client.fail(exceptions.KeyInUse())

        # The client is now connected. We keep the connection open
        # until it disconnects (or sends something).
        try:
            client.send_line('ok')
            client.block_and_disconnect()
        finally:
            # Unsubscribe whatever happens and then re-raise the exception
            self.unpub(key)

    def client_query(self, client, param_str):
        key = param_str.strip()

        client.ensure(is_key(key), exceptions.InvalidKey())

        val = self.query(key)

        client.ensure(val is not None, exceptions.KeyNotFound())

        client.send_line('ok')
        client.send_line(val)

        client.disconnect()

    def client_list(self, client, param_str):
        # TODO use param_str for custom query / prefix selection
        l = self.list()
        client.send_line('ok')
        client.send_line(l)
        client.disconnect()

    def pub(self, key, val):
        if key in self.mapping:
            logger.info("pub denied %s (exists)", {key: val})
            return False
        logger.info("pub %s", {key: val})
        self.mapping[key] = val
        return True

    def unpub(self, key):
        logger.info("unpub %s", key)
        del self.mapping[key]

    def query(self, key):
        return self.mapping.get(key)

    def list(self):
        return ' '.join(sorted(self.mapping.keys()))


class BackgroundServer(Server):
    """A pubres server that forks off to the background.
    Can be started with start(), stopped with stop(),
    and used in a with statement.
    """
    def __init__(self, *args, **kwargs):
        super(BackgroundServer, self).__init__(*args, **kwargs)
        self._server_process = None
        # Just for fail-early assertions
        self._running = False  # TODO use exceptions instead of assertions

    def start(self):
        """Starts the server in a multiprocessing.Process.
        Blocks until the server is accepting connections so that
        callers don't need to wait before using it.

        The server must not be running already; must only be called once.
        """
        # Server should not be running
        assert self._server_process is None
        started_event = multiprocessing.Event()

        def work():
            self.run_until_stop(started_callback=started_event.set)

        self._server_process = multiprocessing.Process(target=work)
        self._server_process.start()

        # Wait for the server to be started
        # Use this wait() loop to terminate early when the _server_process
        # fails with an error; if that happens, the started_event would not
        # be set and we would wait forever.
        while not started_event.is_set() and self._server_process.is_alive():
            started_event.wait(0.01)

        self._running = True

    def stop(self, timeout=None):
        """Stops the server process.

        If timeout is given, returns True iff the server exited within
        the timeout.
        If timeout is None, the server process is guaranteed to exit
        (possibly waiting indefinitely) and True is returned.

        Must only be called after having called start();
        must not be called after the server exited (it returned True).

        Note that when calling this, the server might already have exited
        (e.g. erratically.)
        """
        assert self._running

        # Stop server (does not block)
        super(BackgroundServer, self).stop()

        # Wait for server process to finish
        # This is critical for coverage; if we don't do this,
        # the whole programm will usually exit before the coverage
        # data of the process can be written
        self._server_process.join(timeout)

        if self._server_process.is_alive():
            return False
        else:
            # Guard against repeated calls when server has exited
            self._running = False
            return True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()


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
