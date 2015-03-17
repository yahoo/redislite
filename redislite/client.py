# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
Redislite client

This module contains extended versions of the redis module :class:`Redis()` and
:class:`StrictRedis()` classes.  These classes will set up and run redis on
access and will shutdown and clean up the redis-server when deleted.  Otherwise
they are functionally identical to the :class:`redis.Redis()` and
:class:`redis.StrictRedis()` classes.
"""
import atexit
import json
import logging
import os
import redis
import shutil
import signal
import subprocess
import tempfile
import time
from . import configuration


logger = logging.getLogger(__name__)


class RedisLiteException(Exception):
    pass


class RedisLiteServerStartError(Exception):
    pass


# noinspection PyTypeChecker
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

        command = ['redis-server', config_file]
        logger.debug('Running: %s', ' '.join(command))
        rc = subprocess.call(command)
        if rc:  # pragma: no cover
            raise RedisLiteException('The binary redis-server failed to start')

        # Wait for Redis to start
        timeout = True
        for i in range(0, self.start_timeout * 10):
            if os.path.exists(self.socket_file):
                timeout = False
                break
            time.sleep(.1)
        if timeout:  # pragma: no cover
            raise RedisLiteServerStartError(
                'The redis-server process failed to start'
            )

        if not os.path.exists(self.socket_file):  # pragma: no cover
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
                pid = fh.read().strip()   # NOQA

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

        db_filename = None
        if args:
            db_filename = args[0]

            # Remove our positional argument
            args = args[1:]

        if 'dbfilename' in kwargs.keys():
            db_filename = kwargs['dbfilename']

            # Remove our keyword argument
            del kwargs['dbfilename']

        if db_filename:
            self.dbfilename = os.path.basename(db_filename)
            self.dbdir = os.path.dirname(db_filename)

            self.settingregistryfile = os.path.join(
                self.dbdir, self.dbfilename + '.settings'
            )
            # Remove the argument before we pass it to the redis class

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
    """
    This class provides an enhanced version of the :class:`redis.Redis()` class
    that uses an embedded redis-server by default.


    Example:
        redis_connection = :class:`redislite.Redis('/tmp/redis.db')`


    Notes:
        If the dbfilename argument is not provided each instance will get a
        different redis-server instance.


    Args:
        dbfilename(str):
            The name of the Redis db file to be used.  This argument is only
            used if the embedded redis-server is used.  The value of this
            argument is provided as the "dbfilename" setting in the embedded
            redis server configuration.  This will result in the embedded
            redis server dumping it's database to this file on exit/close.
            This will also result in the embedded redis server using an
            existing redis rdb database if the file exists on start.
            If this file exists and is in use by another redislite instance,
            this class will get a reference to the existing running redis
            instance so both instances share the same redis-server process
            and don't corrupt the db file.

    Kwargs:
        host(str):
            The hostname or ip address of the redis server to connect to.  If
            this argument is not None, the embedded redis server will not be
            used.  Defaults to None.

        port(int): The port number of the redis server to connect to.  If this
            argument is not None, the embedded redis server will not be used.
            Defaults to None.

    Returns:
        A :class:`redis.Redis()` class object if the host or port arguments
        where set or a :class:`redislite.Redis()` object otherwise.

    Raises:
        RedisLiteServerStartError


    Attributes:
        db(string):
            The fully qualified filename associated with the redis dbfilename
            configuration setting.  This attribute is read only.

        pid(int):
            Pid of the running embedded redis server, this attribute is read
            only.

        start_timeout(float):
            Number of seconds to wait for the redis-server process to start
            before generating a RedisLiteServerStartError exception.
    """
    pass


class StrictRedis(RedisMixin, redis.StrictRedis):
    """
    This class provides an enhanced version of the :class:`redis.StrictRedis()`
    class that uses an embedded redis-server by default.


    Example:
        redis_connection = :class:`redislite.StrictRedis('/tmp/redis.db')`


    Notes:
        If the dbfilename argument is not provided each instance will get a
        different redis-server instance.


    Args:
        dbfilename(str):
            The name of the Redis db file to be used.  This argument is only
            used if the embedded redis-server is used.  The value of this
            argument is provided as the "dbfilename" setting in the embedded
            redis server configuration.  This will result in the embedded redis
            server dumping it's database to this file on
            exit/close.  This will also result in the embedded redis server
            using an existing redis database if the file exists on start.
            If this file exists and is in use by another redislite instance,
            this class will get a reference to the existing running redis
            instance so both instances share the same redis-server process
            and don't corrupt the db file.

    Kwargs:
        host(str):
            The hostname or ip address of the redis server to connect to.  If
            this argument is not None, the embedded redis server will not be
            used.  Defaults to None.

        port(int): The
            port number of the redis server to connect to.  If this argument is
            not None, the embedded redis server will not be used.  Defaults to
            None.

    Returns:
        A :class:`redis.StrictRedis()` class object if the host or port
        arguments where set or a :class:`redislite.StrictRedis()` object
        otherwise.

    Raises:
        RedisLiteServerStartError


    Attributes:
        db(string):
            The fully qualified filename associated with the redis dbfilename
            configuration setting.  This attribute is read only.

        pid(int):
            Pid of the running embedded redis server, this attribute is read
            only.

        start_timeout(float):
            Number of seconds to wait for the redis-server process to start
            before generating a RedisLiteServerStartError exception.
    """
    pass
