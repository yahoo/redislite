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
import redislite
import redislite.patch
import shutil
import tempfile
import unittest


# noinspection PyPep8Naming
class TestRedislite(unittest.TestCase):
    def setUp(self):
        pass

    def test_configuration_config(self):
        import redislite.configuration
        result = redislite.configuration.config()
        self.assertIn('\ndaemonize yes', result)

    def test_configuration_settings(self):
        import redislite.configuration
        result = redislite.configuration.settings()
        result_set = set(result.items())
        expected_subset = set(
            {
                'dbdir': './',
                'daemonize': 'yes',
                'unixsocketperm': '700',
                'timeout': '0',
                'dbfilename': 'redis.db'
            }.items()
        )
        self.assertTrue(
            expected_subset.issubset(result_set)
        )

    def test_redislite_Redis(self):
        r = redislite.Redis()
        r.set('key', 'value')
        result = r.get('key').decode(encoding='UTF-8')
        self.assertEqual(result, 'value')

    def test_redislite_Redis_multiple(self):
        r1 = redislite.Redis()
        r2 = redislite.Redis()
        r1.set('key', 'value')
        r2.set('key2', 'value2')
        self.assertTrue(len(r1.keys()), 1)
        self.assertTrue(len(r2.keys()), 1)
        result = r1.get('key').decode(encoding='UTF-8')
        self.assertEqual(result, 'value')
        result = r2.get('key2').decode(encoding='UTF-8')
        self.assertEqual(result, 'value2')

    def test_redislite_Redis_with_db_file(self):
        temp_dir = tempfile.mkdtemp()
        filename = os.path.join(temp_dir, 'redis.db')
        self.assertFalse(os.path.exists(filename))
        r = redislite.Redis(filename)
        r.set('key', 'value')
        result = r.get('key').decode(encoding='UTF-8')
        self.assertEqual(result, 'value')
        r.save()
        r._cleanup()
        self.assertTrue(os.path.exists(filename))
        shutil.rmtree(temp_dir)

    def test_redislite_Redis_multiple_connections(self):
        r = redislite.Redis()       # Generate a new redis server
        s = redislite.Redis(r.db)   # Pass the first server's db to get a
                                    # second connection
        r.set('key', 'value')
        result = s.get('key').decode(encoding='UTF-8')
        self.assertEqual(result, 'value')
        self.assertEqual(r.pid, s.pid)  # Both objects should be using the same
                                        # redis process.

    def test_redislite_Redis_cleanup(self):
        r = redislite.Redis()
        r._cleanup()
        self.assertIsNone(r.socket_file)

    # noinspection PyUnresolvedReferences
    def test_redislite_patch_redis_Redis(self):
        redislite.patch.patch_redis_Redis()
        import redis
        r = redis.Redis()
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid
        redislite.patch.unpatch_redis_Redis()

    def test_redislite_patch_redis_StrictRedis(self):
        redislite.patch.patch_redis_StrictRedis()
        import redis
        r = redis.StrictRedis()
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid
        redislite.patch.unpatch_redis_StrictRedis()

    # noinspection PyUnusedLocal
    def test_redislite_patch_redis(self):
        redislite.patch.patch_redis()
        import redis
        r = redis.Redis()
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid
        s = redis.StrictRedis()
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid
        redislite.patch.unpatch_redis()

    def test_redislite_Redis_create_redis_directory_tree(self):
        r = redislite.Redis()
        r._create_redis_directory_tree()
        self.assertTrue(r.redis_dir)
        self.assertTrue(os.path.exists(r.redis_dir))
        self.assertTrue(os.path.exists(r.pidfile))
        self.assertTrue(os.path.exists(r.socket_file))
        r._cleanup()

    def test_redislite_Redis_pid(self):
        r = redislite.Redis()
        self.assertTrue(r.pidfile)
        self.assertGreater(r.pid, 0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRedislite)
    unittest.TextTestRunner(verbosity=2).run(test_suite)
