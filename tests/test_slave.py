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
        master = redislite.Redis(
            serverconfig={'port': '7000', 'repl-diskless-sync-delay': '0'}
        )
        slave = redislite.Redis(serverconfig={'slaveof': 'localhost 7000'})
        master.set('key', 'value')

        # Redis 7.x defaults to diskless replication, so wait for the sync rather than a fixed delay.
        value = None
        for _ in range(100):
            raw = slave.get('key')
            if raw is not None:
                value = raw.decode(encoding='UTF-8')
                break
            time.sleep(0.1)
        self.assertEqual(value, 'value')
