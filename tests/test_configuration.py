# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
test_redislite
----------------------------------

Tests for `redislite` module.
"""
from __future__ import print_function
import getpass
import inspect
import logging
import os
import redislite
import unittest


logger = logging.getLogger(__name__)


# noinspection PyPep8Naming
class TestRedisliteConfiguration(unittest.TestCase):

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
        import psutil

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

    def test_debug(self):
        import redislite.debug
        redislite.debug.print_debug_info()

    def test_configuration_config(self):
        import redislite.configuration
        result = redislite.configuration.config()
        self.assertIn('\ndaemonize yes', result)


    def test_configuration_modify_defaults(self):
        import redislite.configuration
        result = redislite.configuration.config(daemonize="no")
        self.assertIn('\ndaemonize no', result)

        # ensure the global defaults are not modified
        self.assertEquals(
            redislite.configuration.DEFAULT_REDIS_SETTINGS["daemonize"], "yes"
        )


    def test_configuration_settings(self):
        import redislite.configuration
        result = redislite.configuration.settings()
        del result['save']  # Save is a list which doesn't work with set
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
        self.assertIn('slaveof localhost 6397', result)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_suite = unittest.TestLoader().loadTestsFromTestCase(
        TestRedisliteConfiguration
    )
    unittest.TextTestRunner(verbosity=2).run(test_suite)
