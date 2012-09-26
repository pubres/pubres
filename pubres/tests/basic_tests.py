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


def test_list_empty():
    assert_list([])
    assert_equal(list_str(), '')


def test_list():
    with pub('key1', 'val1'), pub('key2', 'val2'):
        assert_list(['key1', 'key2'])
        assert_equal(list_str(), 'key1 key2')


def test_list_unpub():
    with pub('key1', 'val1'), pub('key2', 'val2'):
        pass
    assert_list([])
    assert_equal(list_str(), '')
