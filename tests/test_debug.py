# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
Tests for `redislite.debug` module.
"""
from __future__ import print_function
import logging
import redislite
import unittest


logger = logging.getLogger(__name__)


# noinspection PyPep8Naming
class TestRedisliteDebug(unittest.TestCase):

    def test_debug(self):
        import redislite.debug
        redislite.debug.print_debug_info()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRedisliteDebug)
    unittest.TextTestRunner(verbosity=2).run(test_suite)
