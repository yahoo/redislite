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
import stat
import tempfile
import unittest


# noinspection PyPep8Naming
class TestRedislite(unittest.TestCase):
    def setUp(self):
        pass

    def test_debug(self):
        import redislite.debug
        redislite.debug.print_debug_info()

    def test_configuration_config(self):
        import redislite.configuration
        result = redislite.configuration.config()
        self.assertIn('\ndaemonize yes', result)
        self.assertIn('\npidfile /var/run/redislite/redis.pid', result)
        self.assertIn('\ntcp-backlog 511', result)



    def test_configuration_config_db(self):
        import redislite.configuration
        result = redislite.configuration.config(
                pidfile='/var/run/redislite/test.pid',
                unixsocket='/var/run/redislite/redis.socket',
                dbdir=os.getcwd(),
                dbfilename='test.db',
        )

        self.assertIn('\ndaemonize yes', result)
        self.assertIn('\npidfile /var/run/redislite/test.pid', result)
        self.assertIn('\ndbfilename test.db', result)

    def test_configuration_config_slave(self):
        import redislite.configuration
        result = redislite.configuration.config(
                pidfile='/var/run/redislite/test.pid',
                unixsocket='/var/run/redislite/redis.socket',
                dbdir=os.getcwd(),
                dbfilename='test.db',
                slaveof='localhost 6397'
        )
        self.assertIn(' slaveof localhost 6397', result)


    def test_configuration_modify_defaults(self):
        import redislite.configuration
        result = redislite.configuration.config(daemonize="no")
        self.assertIn('\ndaemonize no', result)

        # ensure the global defaults are not modified
        self.assertEquals(redislite.configuration.default_settings["daemonize"], "yes")


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

    def test_redislite_Redis_with_db_file_keyword(self):
        temp_dir = tempfile.mkdtemp()
        filename = os.path.join(temp_dir, 'redis.db')
        self.assertFalse(os.path.exists(filename))
        r = redislite.Redis(dbfilename=filename)
        r.set('key', 'value')
        result = r.get('key').decode(encoding='UTF-8')
        self.assertEqual(result, 'value')
        r.save()
        r._cleanup()
        self.assertTrue(os.path.exists(filename))
        shutil.rmtree(temp_dir)

    def test_redislite_Redis_with_serverconfig_dbfile_keyword(self):
        temp_dir = tempfile.mkdtemp()
        filename = os.path.join(temp_dir, 'redis.db')
        self.assertFalse(os.path.exists(filename))
        r = redislite.Redis(serverconfig_dbfilename=filename)
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

        # Pass the first server's db to get a second connection
        s = redislite.Redis(r.db)
        r.set('key', 'value')
        result = s.get('key').decode(encoding='UTF-8')
        self.assertEqual(result, 'value')

        # Both objects should be using the same redis process.
        self.assertEqual(r.pid, s.pid)

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
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid
        s = redis.Redis()
        self.assertIsInstance(r.pid, int)    # Should have a redislite pid

        # Both instances should be talking to the same redis server
        self.assertEqual(r.pid, s.pid)
        redislite.patch.unpatch_redis()

    def test_redislite_Redis_create_redis_directory_tree(self):
        r = redislite.Redis()
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
        r = redislite.Redis(serverconfig_socketfile=socket_file_name)
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
        r = redislite.Redis(serverconfig_socketfile=socket_file_name)
        self.assertEqual(r.socket_file, socket_file_name)
        print(os.listdir('.'))
        mode = os.stat(socket_file_name).st_mode
        isSocket = stat.S_ISSOCK(mode)
        self.assertTrue(isSocket)
        r._cleanup()

    def test_redislite_Redis_pid(self):
        r = redislite.Redis()
        self.assertTrue(r.pidfile)
        self.assertGreater(r.pid, 0)

    def test_redislite_db_file_cwd_args(self):
        test_db = 'test_unit_redis.db'
        if os.path.exists(test_db):
            os.remove(test_db)
        r = redislite.Redis(test_db)
        r.set('key', 'value')
        r.save()
        self.assertTrue(os.path.exists(test_db))
        os.remove(test_db)

    def test_redislite_db_file_cwd_kw(self):
        test_db = 'test_unit_redis.db'
        if os.path.exists(test_db):
            os.remove(test_db)
        r = redislite.Redis(dbfilename=test_db)
        r.set('key', 'value')
        r.save()
        self.assertTrue(os.path.exists(test_db))
        os.remove(test_db)

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
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRedislite)
    unittest.TextTestRunner(verbosity=2).run(test_suite)
