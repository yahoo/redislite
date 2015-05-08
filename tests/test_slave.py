# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
test_redislite
----------------------------------

Tests for `redislite` module.
"""
from __future__ import print_function
import logging
import os
import time
import redis
import redislite
import redislite.patch
import shutil
import stat
import tempfile
import unittest
import subprocess


# noinspection PyPep8Naming
class TestRedisliteSlave(unittest.TestCase):

    def test_slave(self):
        self.master = redislite.Redis(serverconfig={'port': '7000'})
        self.master.set('key', 'value')
        time.sleep(.5)
        s = redislite.Redis(serverconfig={'slaveof': 'localhost 7000'})
        value = s.get('key').decode(encoding='UTF-8')
        self.assertEquals(value, 'value')

