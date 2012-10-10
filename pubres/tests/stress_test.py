from .utils import functions_of_module
from .basic_test import all_simple_tests
import pytest

import pubres


@pytest.mark.slow
def test_multi_server():
    for s in xrange(10):
        with pubres.BackgroundServer():

            simple_tests = all_simple_tests()
            for _ in xrange(10):
                for f in simple_tests:
                    f()
