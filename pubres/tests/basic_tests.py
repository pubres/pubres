from .base import *
from nose.tools import *


def test_subscribe():
    with pub('key1', 'val1'):
        pass


def test_query():
    with pub('key1', 'val1'):
        assert_key_val('key1', 'val1')


def test_unsubscribe():
    with pub('key1', 'val1'):
        pass
    assert_key_not_found(lambda: query('key1'))


def test_pub_query_unsubscribe():
    with pub('key1', 'val1'):
        assert_key_val('key1', 'val1')
        assert_key_not_found(lambda: query('uknownkey'))

    assert_key_not_found(lambda: query('key1'))
