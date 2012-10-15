import logging
import logging.handlers
import multiprocessing

import pubres
from pubres.pubres_logging import setup_logging

from .base import *


# Tests if the logging works.
# Uses a custom logging handler that collects log messages into a list
# and then asserts that they are there.
# Care is taken about the server actually running in a different process.


class MultiprocessingQueueStreamHandler(logging.handlers.BufferingHandler):
    """A logging handler that pushes the getMessage() of every
    LogRecord into a multiprocessing.Queue.

    Used to test log messages of a server started in its own process.
    """
    def __init__(self, *args, **kwargs):
        super(MultiprocessingQueueStreamHandler, self).__init__(*args,
                                                                **kwargs)
        self.mp_logrecord_queue = multiprocessing.Queue()

    # Don't override emit(self, record);
    # BufferingHandler will append record to self.buffer

    def emit(self, record):
        super(MultiprocessingQueueStreamHandler, self).emit(record)
        self.mp_logrecord_queue.put(record.getMessage())

    def getLogRecordBuffer(self):
        ret = []
        while not self.mp_logrecord_queue.empty():
            log = self.mp_logrecord_queue.get()
            ret.append(log)
        return ret


def test_logging():
    # Set up log capturing
    handler = MultiprocessingQueueStreamHandler(10)
    setup_logging(handler=handler)

    # Do some server actions
    with pubres.BackgroundServer():
        with pub('key1', 'val1'):
            pass

    # Make sure actions appear in log
    log_buffer = handler.getLogRecordBuffer()
    assert "pub {'key1': 'val1'}" in log_buffer
