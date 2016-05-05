# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
test_redislite
----------------------------------

Tests for `redislite` module.
"""
from __future__ import print_function
import time
import redislite
import unittest


# noinspection PyPep8Naming
class TestRedisliteSlave(unittest.TestCase):

    def test_slave(self):
        master = redislite.Redis(serverconfig={'port': '7000'})
        slave = redislite.Redis(serverconfig={'slaveof': 'localhost 7000'})
        master.set('key', 'value')
        time.sleep(.5)
        value = slave.get('key').decode(encoding='UTF-8')
        self.assertEquals(value, 'value')
