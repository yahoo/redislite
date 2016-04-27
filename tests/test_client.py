# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
Tests for `redislite.client` module.
"""
from __future__ import print_function
import getpass
import inspect
import logging
import os
import psutil
import redislite
import shutil
import stat
import tempfile
import unittest
from redis.exceptions import ConnectionError


logger = logging.getLogger(__name__)


# noinspection PyPep8Naming
class TestRedisliteClient(unittest.TestCase):

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

    def test_redislite_Redis(self):
        r = redislite.Redis()
        self._log_redis_pid(r)

        r.set('key', 'value')
        result = r.get('key').decode(encoding='UTF-8')
        self.assertEqual(result, 'value')

    def test_redislite_Redis_multiple(self):
        r1 = redislite.Redis()
        r2 = redislite.Redis()
        self._log_redis_pid(r1)
        self._log_redis_pid(r2)

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
        self._log_redis_pid(r)
        r.set('key', 'value')
        result = r.get('key').decode(encoding='UTF-8')
        self.assertEqual(result, 'value')
        r.save()
        r._cleanup()
        self.assertTrue(os.path.exists(filename))
        shutil.rmtree(temp_dir)

    def test_redislite_Redis_with_db_file_keyword(self):
        temp_dir = tempfile.mkdtemp()
        filename = os.path.join(temp_dir, 'redis.db')
        self.assertFalse(os.path.exists(filename))
        r = redislite.Redis(dbfilename=filename)
        self._log_redis_pid(r)
        r.set('key', 'value')
        result = r.get('key').decode(encoding='UTF-8')
        self.assertEqual(result, 'value')
        r.save()
        r._cleanup()
        self.assertTrue(os.path.exists(filename))
        shutil.rmtree(temp_dir)

    def test_redislite_Redis_multiple_connections(self):
        # Generate a new redis server
        r = redislite.Redis()
        self._log_redis_pid(r)

        # Pass the first server's db to get a second connection
        s = redislite.Redis(r.db)
        self._log_redis_pid(s)
        r.set('key', 'value')
        result = s.get('key').decode(encoding='UTF-8')
        self.assertEqual(result, 'value')

        # Both objects should be using the same redis process.
        self.assertEqual(r.pid, s.pid)

    def test_redislite_Redis_cleanup(self):
        r = redislite.Redis()
        self._log_redis_pid(r)
        r._cleanup()
        self.assertIsNone(r.socket_file)

    def test_redislite_Redis_create_redis_directory_tree(self):
        r = redislite.Redis()
        self._log_redis_pid(r)
        r._create_redis_directory_tree()
        self.assertTrue(r.redis_dir)
        self.assertTrue(os.path.exists(r.redis_dir))
        self.assertTrue(os.path.exists(r.pidfile))
        self.assertTrue(os.path.exists(r.socket_file))
        r._cleanup()

    def test_redislite_redis_custom_socket_file_local_directory(self):
        """
        Test creating a redis instance with a specified socket filename
        :return:
        """
        socket_file_name = 'test.socket'
        full_socket_file_name = os.path.join(os.getcwd(), socket_file_name)
        r = redislite.Redis(unix_socket_path=socket_file_name)
        self._log_redis_pid(r)
        self.assertEqual(r.socket_file, full_socket_file_name)
        print(os.listdir('.'))
        mode = os.stat(socket_file_name).st_mode
        isSocket = stat.S_ISSOCK(mode)
        self.assertTrue(isSocket)
        r._cleanup()

    def test_redislite_redis_custom_socket_file(self):
        """
        Test creating a redis instance with a specified socket filename
        :return:
        """
        socket_file_name = '/tmp/test.socket'
        r = redislite.Redis(unix_socket_path=socket_file_name)
        self._log_redis_pid(r)
        self.assertEqual(r.socket_file, socket_file_name)
        print(os.listdir('.'))
        mode = os.stat(socket_file_name).st_mode
        isSocket = stat.S_ISSOCK(mode)
        self.assertTrue(isSocket)
        r._cleanup()

    def test_redislite_Redis_pid(self):
        r = redislite.Redis()
        self._log_redis_pid(r)
        self.assertTrue(r.pidfile)
        self.assertGreater(r.pid, 0)

    def test_redislite_db_file_cwd_args(self):
        test_db = 'test_unit_redis.db'
        if os.path.exists(test_db):
            os.remove(test_db)
        r = redislite.Redis(test_db)
        self._log_redis_pid(r)
        r.set('key', 'value')
        r.save()
        self.assertTrue(os.path.exists(test_db))
        os.remove(test_db)

    def test_redislite_db_file_cwd_kw(self):
        test_db = 'test_unit_redis.db'
        if os.path.exists(test_db):
            os.remove(test_db)
        r = redislite.Redis(dbfilename=test_db)
        self._log_redis_pid(r)
        r.set('key', 'value')
        r.save()
        self.assertTrue(os.path.exists(test_db))
        os.remove(test_db)

    def test_is_redis_running_no_pidfile(self):
        r = redislite.Redis()
        self._log_redis_pid(r)
        r.shutdown()
        result = r._is_redis_running()
        self.assertFalse(result)

    def test_refcount_cleanup(self):
        self.logger.debug('Setting up 2 connections to a single redis server.')
        r = redislite.Redis()
        self._log_redis_pid(r)
        s = redislite.Redis(r.db)
        self._log_redis_pid(s)

        pid = r.pid
        redis_dir = r.redis_dir

        self.logger.debug('Making sure the redis-server is running')
        p = psutil.Process(pid)
        self.assertTrue(p.is_running())

        self.logger.debug(
            'Shuting down the first instance, redis-server should remain '
            'running due to the other connection.'
        )
        r._cleanup()

        self.assertTrue(
            os.path.exists(redis_dir),
            msg='Shutting down the server removed the temporary directory'
        )
        self.assertEqual(
            s.pid, pid,
            msg='Redis server shutdown with active connection'
        )

        p = psutil.Process(pid)
        self.assertTrue(
            p.is_running(),
            msg='Redis server shutdown with active connection'
        )

        self.logger.debug(
            'Shutting down  the second instance, the redis-server should '
            'be gone after the connection terminates'
        )
        self.logger.debug(
            'Second connection count is: %s', s._connection_count()
        )
        s._cleanup()
        with self.assertRaises(psutil.NoSuchProcess):
            p = psutil.Process(pid)

    def test_connection_count(self):
        r = redislite.Redis()
        self._log_redis_pid(r)
        self.assertEqual(r._connection_count(), 1)

    def test_connection_count_multiple(self):
        r = redislite.Redis()
        self._log_redis_pid(r)
        s = redislite.Redis(r.db)
        self.assertEqual(r._connection_count(), 2)

    def test_connection_fallthrough(self):
        """
        Create a connection with an argument that will cause redislite
        to pass it to the redis module.  This should generate an exception
        since there is no redis server running on the port.
        :return:
        """
        with self.assertRaises(ConnectionError):
            redislite.Redis(port=1).keys()

    def test_shutdown_race_condition(self):
        """
        Test that there is no race condition when a shutdown is run after
        a large data operation.
        """
        if os.path.exists('bug.redis'):
            os.remove('bug.redis')
        db = redislite.StrictRedis('bug.redis')
        for key in range(10000):
            db.hset("h1", os.urandom(32), " " * 65536)
        db.save()
        db._cleanup()
        del db
        db = redislite.StrictRedis('bug.redis')
        if os.path.exists('bug.redis'):
            os.remove('bug.redis')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_suite = unittest.TestLoader().loadTestsFromTestCase(
        TestRedisliteClient
    )
    unittest.TextTestRunner(verbosity=2).run(test_suite)
