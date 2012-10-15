from .base import *
from .utils import functions_of_module
from nose.tools import *
import pytest

import pubres


# TODO decide if this global is nice or not.
test_server = None

def setup_module(module):
    global test_server
    test_server = pubres.BackgroundServer()
    test_server.start()

def teardown_module(module):
    global test_server
    test_server.stop()



def test_simple_subscribe():
    with pub('key1', 'val1'):
        pass


def test_simple_query():
    with pub('key1', 'val1'):
        assert_key_val('key1', 'val1')


def test_simple_unsubscribe():
    with pub('key1', 'val1'):
        pass
    assert_key_not_found(lambda: query('key1'))


def test_simple_pub_query_unsubscribe():
    with pub('key1', 'val1'):
        assert_key_val('key1', 'val1')
        assert_key_not_found(lambda: query('uknownkey'))

    assert_key_not_found(lambda: query('key1'))


def test_simple_list_empty():
    assert_list([])
    assert_equal(list_str(), '')


def test_simple_list():
    with pub('key1', 'val1'), pub('key2', 'val2'):
        assert_list(['key1', 'key2'])
        assert_equal(list_str(), 'key1 key2')


def test_simple_list_unpub():
    with pub('key1', 'val1'), pub('key2', 'val2'):
        pass
    assert_list([])
    assert_equal(list_str(), '')


def test_invalid_action():
    s = connect()
    s.sendall('someunknowncommand\n')
    fp = s.makefile()
    answer = fp.readline(128)
    assert answer == "invalid action\n"


def test_key_in_use():
    with pub('key1', 'val1'):
        with pytest.raises(PubFailed) as ex:
            with pub('key1', 'val1_2'):
                pass  # Exception will raise here
        assert ex.value.server_message == 'key in use'


def all_simple_tests():
    is_simple = lambda n: n.startswith('test_simple_')
    return functions_of_module(__name__, is_simple)


# Runs all other "test_"s via inspection.
@pytest.mark.slow
def test_all_repeated():
    """Runs all other tests defined in this module, many times.
    """
    simple_tests = all_simple_tests()
    for x in xrange(100):
        for f in simple_tests:
            f()
