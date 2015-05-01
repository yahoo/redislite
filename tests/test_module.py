# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
Tests for `redislite` module (__init__.py).
"""
from __future__ import print_function
import logging
import redislite
import redislite.patch
import unittest


logger = logging.getLogger(__name__)


# noinspection PyPep8Naming
class TestRedisliteModule(unittest.TestCase):
    def test_metadata(self):
        self.assertIsInstance(redislite.__version__, str)
        self.assertIsInstance(redislite.__git_version__, str)
        self.assertIsInstance(redislite.__git_origin__, str)
        self.assertIsInstance(redislite.__git_branch__, str)
        self.assertIsInstance(redislite.__git_hash__, str)
        self.assertIsInstance(redislite.__redis_server_info__, dict)
        self.assertIsInstance(redislite.__redis_executable__, str)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_suite = unittest.TestLoader().loadTestsFromTestCase(
        TestRedisliteModule
    )
    unittest.TextTestRunner(verbosity=2).run(test_suite)
