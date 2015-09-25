# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
Tests for `redislite.patch` module.
"""
from __future__ import print_function
import getpass
import inspect
import logging
import os
import psutil
import redislite
import redislite.patch
import unittest


logger = logging.getLogger(__name__)


# noinspection PyPep8Naming
class TestRedislitePatch(unittest.TestCase):

    class logger(object):
        @staticmethod
        def debug(*args, **kwargs):
            new_args = list(args)
            new_args[0] = str(inspect.stack()[1][3]) + ': ' + new_args[0]
            args=tuple(new_args)
            return logger.debug(*args, **kwargs)

    def _redis_server_processes(self):
        """
        Return count of process objects for all redis-server processes started
        by the current user.
        :return:
        """
        processes = []
        for proc in psutil.process_iter():
            try:
                if proc.name() == 'redis-server':
                    if proc.username() == getpass.getuser():
                        processes.append(proc)
            except psutil.NoSuchProcess:
                pass

        return len(processes)

    def _log_redis_pid(self, connection):
        logger.debug(
            '%s: r.pid: %d', str(inspect.stack()[1][3]), connection.pid
        )

    def setUp(self):
        logger.info(
            'Start Child processes: %d', self._redis_server_processes()
        )

    def tearDown(self):
        logger.info(
            'End Child processes: %d', self._redis_server_processes()
        )

    def test_redislite_patch_redis_Redis(self):
        redislite.patch.patch_redis_Redis()
        import redis
        r = redis.Redis()
        self._log_redis_pid(r)
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid
        redislite.patch.unpatch_redis_Redis()

    def test_redislite_patch_redis_StrictRedis(self):
        redislite.patch.patch_redis_StrictRedis()
        import redis
        r = redis.StrictRedis()
        self._log_redis_pid(r)
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid
        redislite.patch.unpatch_redis_StrictRedis()

    # noinspection PyUnusedLocal
    def test_redislite_patch_redis(self):
        redislite.patch.patch_redis()
        import redis
        r = redis.Redis()
        self._log_redis_pid(r)
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid
        s = redis.StrictRedis()
        self._log_redis_pid(s)
        self.assertIsInstance(s.pid, int)    # Should have a redislite pid
        redislite.patch.unpatch_redis()

    def test_redislite_double_patch_redis(self):
        import redis
        original_redis = redis.Redis
        redislite.patch.patch_redis()
        self.assertNotEqual(original_redis, redis.Redis)
        redislite.patch.patch_redis()
        self.assertNotEqual(original_redis, redis.Redis)
        redislite.patch.unpatch_redis()
        self.assertEqual(original_redis, redis.Redis)

    def test_redislite_patch_redis_with_dbfile(self):
        dbfilename = '/tmp/test_redislite_patch_redis_with_dbfile.db'
        if os.path.exists(dbfilename):
            os.remove(dbfilename)
        redislite.patch.patch_redis(dbfilename)
        import redis
        r = redis.Redis()
        self._log_redis_pid(r)
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid
        s = redis.Redis()
        self._log_redis_pid(s)
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid

        # Both instances should be talking to the same redis server
        self.assertEqual(r.pid, s.pid)
        redislite.patch.unpatch_redis()

    def test_redislite_patch_strictredis_with_dbfile(self):
        dbfilename = 'test_redislite_patch_redis_with_short_dbfile.db'
        if os.path.exists(dbfilename):
            os.remove(dbfilename)
        redislite.patch.patch_redis_StrictRedis(dbfilename)
        import redis
        r = redis.StrictRedis()
        self._log_redis_pid(r)
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid
        s = redis.StrictRedis()
        self._log_redis_pid(s)
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid

        # Both instances should be talking to the same redis server
        self.assertEqual(r.pid, s.pid)
        redislite.patch.unpatch_redis_StrictRedis()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRedislitePatch)
    unittest.TextTestRunner(verbosity=2).run(test_suite)
