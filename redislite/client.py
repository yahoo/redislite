# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
from __future__ import print_function
import atexit
import json
import logging
import os
import redis
import shutil
import signal
import tempfile
import time
from . import configuration
"""
Redislite client

This module contains extended versions of the redis module Redis() and
StrictRedis() classes.  These classes will set up and run redis on access and
will shutdown and clean up the redis-server when deleted.  Otherwise they are
functionally identical to the redis.Redis() and redis.StrictRedis() classes.
"""


logger = logging.getLogger(__name__)


class RedisLiteException(Exception):
    pass


class RedisMixin(object):
    """
    Extended version of the redis.Redis class with code to start/stop the
    embedded redis server based on the passed arguments.
    """
    redis_dir = None
    pidfile = None
    socket_file = None
    connection = None
    start_timeout = 10
    running = False
    dbfilename = 'redis.db'
    dbdir = None
    settingregistryfile = None
    cleanupregistry = False

    def _cleanup(self):
        """
        Stop the redis-server for this instance if it's running
        :return:
        """

        if not self.redis_dir:
            return

        if self.running:
            logger.debug(
                'Shutting down the redis connection on socket: %s',
                self.socket_file
            )
            # noinspection PyUnresolvedReferences
            logger.debug(
                'Shutting down redis server with pid of %d' % self.pid)
            self.shutdown()
            self.socket_file = None

        if self.pidfile and os.path.exists(self.pidfile):   # pragma: no cover
            # noinspection PyTypeChecker
            pid = int(open(self.pidfile).read())
            os.kill(pid, signal.SIGKILL)

        if os.path.isdir(self.redis_dir):  # pragma: no cover
            shutil.rmtree(self.redis_dir)

        if self.cleanupregistry and os.path.exists(self.settingregistryfile):
            os.remove(self.settingregistryfile)
            self.settingregistryfile = None

        self.running = False
        self.redis_dir = None
        self.pidfile = None

    def _create_redis_directory_tree(self):
        """
        Create a temp directory for holding our self contained redis instance.
        :return:
        """
        if not self.redis_dir:
            self.redis_dir = tempfile.mkdtemp()
            logger.debug(
                'Creating temporary redis directory %s', self.redis_dir
            )
            self.pidfile = os.path.join(self.redis_dir, 'redis.pid')
            self.socket_file = os.path.join(self.redis_dir, 'redis.socket')

    def _start_redis(self):
        """
        Start the redis server
        :return:
        """
        config_file = os.path.join(self.redis_dir, 'redis.config')

        # Write a redis.config to our temp directory
        fh = open(config_file, 'w')
        fh.write(
            configuration.config(
                pidfile=self.pidfile,
                unixsocket=self.socket_file,
                dbdir=self.dbdir,
                dbfilename=self.dbfilename
            )
        )
        fh.close()

        command = 'redis-server %s' % config_file
        logger.debug('Running: %s', command)
        rc = os.system(command) >> 8
        if rc:  # pragma: no cover
            raise RedisLiteException('The binary redis-server failed to start')

        # Wait for Redis to start
        timeout = True
        for i in range(0, self.start_timeout):
            if os.path.exists(self.socket_file):
                timeout = False
                break
            time.sleep(1)
        if timeout:  # pragma: no cover
            raise RedisLiteException(
                'The redis-server process failed to start'
            )

        if not os.path.exists(self.socket_file):  # pragma: no cover
            os.system('ps auxwwww | grep redis-server')
            if os.path.exists(self.pidfile):
                os.system('lsof -p %s' % open(self.pidfile).read().strip())
            raise RedisLiteException(
                'Redis socket file %s is not present' % self.socket_file
            )
        self._save_setting_registry()
        self.running = True

    def _is_redis_running(self):
        """
        Determine if there is a config setting for a currently running redis
        :return:
        """
        if not self.settingregistryfile:
            return False

        if os.path.exists(self.settingregistryfile):
            with open(self.settingregistryfile) as fh:
                settings = json.load(fh)
            with open(settings['pidfile']) as fh:
                pid = fh.read().strip()

            return True
        return False

    def _save_setting_registry(self):
        """
        Save the settings config to the registry file
        :return:
        """
        settings = {
            'pidfile': self.pidfile,
            'unixsocket': self.socket_file,
            'dbdir': self.dbdir,
            'dbfilename': self.dbfilename,
        }
        with open(self.settingregistryfile, 'w') as fh:
            os.fchmod(fh.fileno(), 0o0600)  # Only owner can access
            json.dump(settings, fh)
        self.cleanupregistry = True

    def _load_setting_registry(self):
        """
        Load the settings config from a registry file
        :return:
        """
        with open(self.settingregistryfile) as fh:
            settings = json.load(fh)
        self.pidfile = settings['pidfile']
        self.socket_file = settings['unixsocket']
        self.dbdir = settings['dbdir']
        self.dbfilename = settings['dbfilename']

    def __init__(self, *args, **kwargs):
        """
        Wrapper for redis.Redis that configures a redis instance based on the
        passed settings.
        :param args:
        :param kwargs:
        :return:
        """
        # If the user is specifying settings we can't configure just pass the
        # request to the redis.Redis module
        if 'host' in kwargs.keys() or 'port' in kwargs.keys():
            # noinspection PyArgumentList,PyPep8
            super(RedisMixin, self).__init__(*args, **kwargs)  # pragma: no cover

        if args:
            self.dbfilename = os.path.basename(args[0])
            self.dbdir = os.path.dirname(args[0])

            self.settingregistryfile = os.path.join(
                self.dbdir, self.dbfilename + '.settings'
            )

        if self._is_redis_running():
            self._load_setting_registry()
        else:
            self._create_redis_directory_tree()

            if not self.dbdir:
                self.dbdir = self.redis_dir
                self.settingregistryfile = os.path.join(
                    self.dbdir, self.dbfilename + '.settings'
                )

            atexit.register(self._cleanup)

            self._start_redis()

        kwargs['unix_socket_path'] = self.socket_file
        # noinspection PyArgumentList
        super(RedisMixin, self).__init__(*args, **kwargs)  # pragma: no cover

    def __del__(self):
        self._cleanup()

    @property
    def db(self):
        """
        Return the connection string to allow connecting to the same redis
        server.
        :return: connection_path
        """
        return os.path.join(self.dbdir, self.dbfilename)

    @property
    def pid(self):
        if self.pidfile:
            with open(self.pidfile) as fh:
                pid = fh.read().strip()
            return int(pid)
        return None  # pragma: no cover

class Redis(RedisMixin, redis.Redis):
    pass


class StrictRedis(RedisMixin, redis.StrictRedis):
    pass

