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
import psutil
import redis
import shutil
import signal
import subprocess
import tempfile
import time
import sys
from . import configuration
from . import __redis_executable__


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class RedisLiteException(Exception):
    """
    Redislite Client Error exception class
    """
    pass


class RedisLiteServerStartError(Exception):
    """
    Redislite redis-server start error
    """
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
    redis_configuration = None
    redis_configuration_filename = None

    def _cleanup(self, sys_modules=None):
        """
        Stop the redis-server for this instance if it's running
        :return:
        """
        if sys_modules:     # pragma: no cover
            import sys
            sys.modules.update(sys_modules)

        if self.pid:
            # logger.debug('Connection count: %s', self._connection_count())
            if self._connection_count() <= 1:
                logger.debug(
                    'Last client using the connection, shutting down the '
                    'redis connection on socket: %s',
                    self.socket_file
                )
                # noinspection PyUnresolvedReferences
                logger.debug(
                    'Shutting down redis server with pid of %r', self.pid
                )
                try:
                    self.shutdown(save=True, now=True, force=True)
                    try:  # pragma: no cover
                        process = psutil.Process(self.pid)
                    except psutil.NoSuchProcess:  # pragma: no cover
                        process = None
                    if process:   # pragma: no cover
                        for i in range(50):
                            if not process.is_running():
                                break
                            time.sleep(.2)
                except redis.RedisError:  # pragma: no cover
                    if self.pid != 0:
                        try:
                            process = psutil.Process(self.pid)
                            if process.is_running() and process.pid != 0:
                                logger.info(f'Redis shutdown failed, sending sigterm to {self.pid}')
                                os.kill(self.pid, signal.SIGTERM)
                                for i in range(120):  # default shutdown timeout is 10 seconds
                                    if not process.is_running():
                                        break
                                    time.sleep(.1)
                            if process.is_running() and process.pid != 0:
                                logger.warning('Redis graceful shutdown failed, forcefully killing pid %r', self.pid)
                                os.kill(self.pid, signal.SIGKILL)
                        except psutil.NoSuchProcess:
                            pass
                self.socket_file = None

                if self.pidfile and os.path.exists(
                        self.pidfile
                ):   # pragma: no cover
                    # noinspection PyTypeChecker
                    pid = int(open(self.pidfile).read())
                    try:
                        process = psutil.Process(pid)
                        if process.is_running():
                            os.kill(pid, signal.SIGKILL)
                    except psutil.NoSuchProcess:
                        pass

                if self.redis_dir and os.path.isdir(
                        self.redis_dir
                ):  # pragma: no cover
                    shutil.rmtree(self.redis_dir)

                if self.cleanupregistry and os.path.exists(
                        self.settingregistryfile
                ):
                    os.remove(self.settingregistryfile)
                    self.settingregistryfile = None
            else:
                logger.debug(
                    'Other clients are still connected to the redis server, '
                    'not shutting down the connection on socket: %s',
                    self.socket_file
                )
                self.connection_pool.disconnect()

        self.running = False
        self.redis_dir = None
        self.pidfile = None

    def _connection_count(self):
        """
        Return the number of active connections to the redis server.
        :return:
        """
        if not self._is_redis_running():  # pragma: no cover
            return 0

        active_connections = 0
        client_list = self.client_list()
        if not client_list:  # pragma: no cover
            return 0

        for client in client_list:
            flags = client.get('flags', '')
            flags = flags.upper()
            if 'U' in flags or 'N' in flags:  # pragma: no cover
                active_connections += 1
        return active_connections

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
            self.logfile = os.path.join(self.redis_dir, 'redis.log')
            if not self.socket_file:
                self.socket_file = os.path.join(self.redis_dir, 'redis.socket')

    def _start_redis(self):
        """
        Start the redis server
        :return:
        """

        self.redis_configuration_filename = os.path.join(
            self.redis_dir, 'redis.config'
        )

        kwargs = dict(self.server_config)
        kwargs.update(
            {
                'pidfile': self.pidfile,
                'logfile': kwargs.get('logfile', self.logfile),
                'unixsocket': self.socket_file,
                'dbdir': self.dbdir,
                'dbfilename': self.dbfilename
            }
        )
        # Write a redis.config to our temp directory
        self.redis_configuration = configuration.config(**kwargs)
        with open(self.redis_configuration_filename, 'w') as file_handle:
            file_handle.write(self.redis_configuration)

        redis_executable = __redis_executable__
        if not redis_executable:  # pragma: no cover
            redis_executable = 'redis-server'
        command = [redis_executable, self.redis_configuration_filename]
        logger.debug('Running: %s', ' '.join(command))
        rc = subprocess.call(command)
        if rc:  # pragma: no cover
            logger.debug('The binary redis-server failed to start')
            logger.debug('Redis Server log:\n%s', self.redis_log)
            raise RedisLiteException('The binary redis-server failed to start')

        # Wait for Redis to start
        timeout = True
        for i in range(0, self.start_timeout * 10):
            if os.path.exists(self.socket_file):
                timeout = False
                break
            time.sleep(.1)
        if timeout:  # pragma: no cover
            logger.debug('Redis Server log:\n%s', self.redis_log)
            raise RedisLiteServerStartError(
                'The redis-server process failed to start'
            )

        if not os.path.exists(self.socket_file):  # pragma: no cover
            logger.debug('Redis Server log:\n%s', self.redis_log)
            raise RedisLiteException(
                'Redis socket file %s is not present' % self.socket_file
            )

        self._save_setting_registry()
        self.running = True

    def _wait_for_server_start(self):
        """
        Wait until the server is not busy when receiving a request

        Raises
        ------
        RedisLiteServerStartError - Server start timed out
        """
        timeout = True
        for i in range(0, self.start_timeout * 10):
            try:
                self.ping()
                timeout = False
                break
            except redis.BusyLoadingError:
                pass
            time.sleep(.1)
        if timeout:  # pragma: no cover
            raise RedisLiteServerStartError(
                'The redis-server process failed to start; unreachable after '
                '{0} seconds'.format(self.start_timeout)
            )

    def _is_redis_running(self):
        """
        Determine if there is a config setting for a currently running redis
        :return:
        """
        if not self.settingregistryfile:
            return False

        if os.path.exists(self.settingregistryfile):
            with open(self.settingregistryfile) as file_handle:
                settings = json.load(file_handle)

            if not os.path.exists(settings['pidfile']):
                return False

            with open(settings['pidfile']) as file_handle:
                pid = file_handle.read().strip()   # NOQA
                pid = int(pid)
                if pid:  # pragma: no cover
                    try:
                        process = psutil.Process(pid)
                    except psutil.NoSuchProcess:
                        return False
                    if not process.is_running():
                        return False
                else:  # pragma: no cover
                    return False
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
        logger.debug('loading settings, found: %s', settings)
        pidfile = settings.get('pidfile', '')
        if os.path.exists(pidfile):
            # noinspection PyUnusedLocal
            pid_number = 0
            with open(pidfile) as fh:
                pid_number = int(fh.read())
            if pid_number:
                process = psutil.Process(pid_number)
                if not process.is_running():  # pragma: no cover
                    logger.warning(
                        'Loaded registry for non-existent redis-server'
                    )
                    return
        else:  # pragma: no cover
            logger.warning('No pidfile found')
            return
        self.pidfile = settings['pidfile']
        self.socket_file = settings['unixsocket']
        self.dbdir = settings['dbdir']
        self.dbfilename = settings['dbfilename']

    def __init__(self, *args, **kwargs):
        """
        Wrapper for redis.Redis that configures a redis instance based on the
        passed settings.

        Parameters
        ==========
        db_filename : str, optional
            Path to the redis rdb file to back the redis instance, if not
            specified one will be created inside a temporary directory for
            the instance.

        serverconfig : dict, optional
            A dict containing redis server settings.  The key is the setting
            the value can be a string, list or None.

            If the value is a string it will be used as the value in the redis
            configuration.

            If the value is a list the same setting will be repeated multiple
            times in the redis configuration with each value in order.

            If the value is None, the setting will be removed from the
            default configuration if it is set.
        """
        # If the user is specifying settings we can't configure just pass the
        # request to the redis.Redis module
        if 'host' in kwargs.keys() or 'port' in kwargs.keys():
            # noinspection PyArgumentList
            super(RedisMixin, self).__init__(
                *args, **kwargs
            )  # pragma: no cover
            return

        self.socket_file = kwargs.get('unix_socket_path', None)
        if self.socket_file and self.socket_file == os.path.basename(
                self.socket_file
        ):
            self.socket_file = os.path.join(os.getcwd(), self.socket_file)

        db_filename = None
        if args:
            db_filename = args[0]

            # Remove our positional argument
            args = args[1:]

        if 'dbfilename' in kwargs.keys():
            db_filename = kwargs['dbfilename']

            # Remove our keyword argument
            del kwargs['dbfilename']

        self.server_config = kwargs.pop('serverconfig', {})

        if db_filename and db_filename == os.path.basename(db_filename):
            db_filename = os.path.join(os.getcwd(), db_filename)

        if db_filename:
            self.dbfilename = os.path.basename(db_filename)
            self.dbdir = os.path.dirname(db_filename)

            self.settingregistryfile = repr(os.path.join(
                self.dbdir, self.dbfilename + '.settings'
            )).strip("'")

        logger.debug('Setting up redis with rdb file: %s', self.dbfilename)
        logger.debug('Setting up redis with socket file: %s', self.socket_file)
        atexit.register(self._cleanup, sys.modules.copy())
        if self._is_redis_running() and not self.socket_file:
            self._load_setting_registry()
            logger.debug(
                'Socket file after registry load: %s', self.socket_file
            )
        else:
            self._create_redis_directory_tree()

            if not self.dbdir:
                self.dbdir = self.redis_dir
                self.settingregistryfile = repr(os.path.join(
                    self.dbdir, self.dbfilename + '.settings'
                )).strip("'")
            self._start_redis()

        kwargs['unix_socket_path'] = self.socket_file
        # noinspection PyArgumentList
        logger.debug('Calling binding with %s, %s', args, kwargs)
        # noinspection PyArgumentList
        super(RedisMixin, self).__init__(*args, **kwargs)  # pragma: no cover

        logger.debug("Pinging the server to ensure we're connected")
        self._wait_for_server_start()

    def __del__(self):
        self._cleanup()  # pragma: no cover

    def redis_log_tail(self, lines=1, width=80):
        """
        The redis log output


        Parameters
        ----------
        lines : int, optional
            Number of lines from the end of the logfile to return, a value of
            0 will return all lines, default=1

        width : int, optional
            The expected average width of a log file line, this is used to
            determine the chunksize of the seek operations, default=80

        Returns
        -------
        list
            List of strings containing the lines from the logfile requested
        """
        chunksize = lines * width

        if not os.path.exists(self.logfile):
            return []

        with open(self.logfile) as log_handle:
            if lines == 0:
                return [_.strip() for _ in log_handle.readlines()]
            log_handle.seek(0, 2)
            log_size = log_handle.tell()
            if log_size == 0:
                logger.debug('Logfile %r is empty', self.logfile)
                return []
            data = []
            for increment in range(1, int(log_size / chunksize) + 1):
                seek_location = max(chunksize * increment, 0)
                log_handle.seek(seek_location, 0)
                data = log_handle.readlines()
                if len(data) >= lines:
                    return [_.strip() for _ in data[-lines:]]
            return [_.strip() for _ in data]

    @property
    def redis_log(self):
        """
        Redis server log content as a string

        Returns
        -------
        str
            Log contents
        """
        return os.linesep.join(self.redis_log_tail(lines=0))

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
        """
        Get the current redis-server process id.

        Returns:
            pid(int):
                The process id of the redis-server process associated with this
                redislite instance or None.  If the redis-server is not
                running.
        """
        if self.pidfile and os.path.exists(self.pidfile):
            with open(self.pidfile) as file_handle:
                pid = int(file_handle.read().strip())
                if pid:  # pragma: no cover
                    try:
                        process = psutil.Process(pid)
                    except psutil.NoSuchProcess:
                        return 0
                    if not process.is_running():
                        return 0
                else:  # pragma: no cover
                    return 0
            return int(pid)
        return 0  # pragma: no cover


class BaseRedis(redis.Redis):
    pass

# noinspection PyUnresolvedReferences
class Redis(RedisMixin, BaseRedis):
    """
    This class provides an enhanced version of the :class:`redis.Redis()` class
    that uses an embedded redis-server by default.


    Parameters
    ----------

    dbfilename : str, optional

        The name of the Redis db file to be used.

        This argument is only used if the embedded redis-server is used.

        The value of this argument is provided as the "dbfilename" setting in
        the embedded redis server configuration.  This will result in the
        embedded redis server dumping it's database to this file on exit/close.

        This will also result in the embedded redis server using an
        existing redis rdb database if the file exists on start.

        If this file exists and is in use by another redislite instance,
        this class will get a reference to the existing running redis
        instance so both instances share the same redis-server process
        and don't corrupt the db file.

    serverconfig : dict, optional

        A dictionary of additional redis-server configuration settings.
        The key is the name of the setting in the configuration file, the
        values may be list, str, or None.

        If the value is a list the setting will be repeated in the
        configuration, once for each value.

        If the value is a string, the setting will occur once with that string
        as the setting.

        If the value is None, the setting will be removed from the default
        setting values if it exists in the defaults.

    host : str, optional

        The hostname or ip address of the redis server to connect to.

        If this argument is specified the embedded redis server will not be
        used.

    port : int, optional

        The port number of the redis server to connect to.

        If this argument is specified, the embedded redis server will not be
        used.

    **kwargs : optional
        All other keyword arguments supported by the :py:class:`redis.Redis()`
        class are supported.

    Returns
    -------

    A :class:`redislite.Redis()` object

    Raises
    ------

    RedisLiteServerStartError
        The embedded Redis server failed to start

    Example
    -------

    redis_connection = :class:`redislite.Redis('/tmp/redis.db')`

    Notes
    -----

    If the dbfilename argument is not provided each instance will get a
    different redis-server instance.


    Attributes
    ----------

    db : str
        The fully qualified filename associated with the redis dbfilename
        configuration setting.  This attribute is read only.

    logfile : str
        The name of the redis-server logfile

    pid :int
        Pid of the running embedded redis server, this attribute is read
        only.

    redis_log : str
        The contents of the redis-server log file

    start_timeout : float
        Number of seconds to wait for the redis-server process to start
        before generating a RedisLiteServerStartError exception.
    """
    pass


class BaseStrictRedis(redis.StrictRedis):
    pass


# noinspection PyUnresolvedReferences
class StrictRedis(RedisMixin, BaseStrictRedis):
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

        serverconfig(dict): A dictionary of additional redis-server
            configuration settings.  All keys and values must be str.
            Supported keys are:
                activerehashing,
                aof_rewrite_incremental_fsync,
                appendfilename,
                appendfsync,
                appendonly,
                auto_aof_rewrite_min_size,
                auto_aof_rewrite_percentage,
                aof_load_truncated,
                databases,
                hash_max_ziplist_entries,
                hash_max_ziplist_value,
                hll_sparse_max_bytes,
                hz,
                latency_monitor_threshold,
                list_max_ziplist_entries,
                list_max_ziplist_value,
                logfile,
                loglevel,
                lua_time_limit,
                no_appendfsync_on_rewrite,
                notify_keyspace_events,
                port,
                rdbchecksum,
                rdbcompression,
                repl_disable_tcp_nodelay,
                slave_read_only,
                slave_serve_stale_data,
                stop_writes_on_bgsave_error,
                tcp_backlog,
                tcp_keepalive,
                unixsocket,
                unixsocketperm,
                slave_priority,
                timeout,
                set_max_intset_entries,
                zset_max_ziplist_entries,
                zset_max_ziplist_value

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
