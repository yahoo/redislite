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


    def setUp(self):
        subprocess.call("redis-server --port 7000 --daemonize yes --pidfile redis_master.pid".split())

        self.r = redis.Redis(port=7000)
        self.r.set('key', 'value')


    def tearDown(self):
        self.r.shutdown()



    def test_slave(self):
        s = redislite.Redis(serverconfig={'slaveof': 'localhost 7000'})

        value = s.get('key').decode(encoding='UTF-8')
        self.assertEquals(value, 'value')

