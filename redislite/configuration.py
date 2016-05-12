# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
This module contains functions to generate a redis configuration from a
configuration template.
"""
import logging
from copy import copy


logger = logging.getLogger(__name__)  # pylint: disable=C0103


DEFAULT_REDIS_SETTINGS = {
    'activerehashing': 'yes',
    'aof-rewrite-incremental-fsync': 'yes',
    'appendonly': 'no',
    'appendfilename': 'appendonly.aof',
    'appendfsync': 'everysec',
    'aof-load-truncated': 'yes',
    'auto-aof-rewrite-percentage': '100',
    'auto-aof-rewrite-min-size': '64mb',
    'bind': None,
    'daemonize': 'yes',
    'databases': '16',
    'dbdir': './',
    'dbfilename': 'redis.db',
    'hash-max-ziplist-entries': '512',
    'hash-max-ziplist-value': '64',
    'hll-sparse-max-bytes': '3000',
    'hz': '10',
    'list-max-ziplist-entries': '512',
    'list-max-ziplist-value': '64',
    'loglevel': 'notice',
    'logfile' : 'redis.log',
    'lua-time-limit': '5000',
    'pidfile': '/var/run/redislite/redis.pid',
    'port': '0',
    'save': ['900 1', '300 100', '60 200', '15 1000'],
    'stop-writes-on-bgsave-error': 'yes',
    'tcp-backlog': '511',
    'tcp-keepalive': '0',
    'rdbcompression': 'yes',
    'rdbchecksum': 'yes',
    'slave-serve-stale-data': 'yes',
    'slave-read-only': 'yes',
    'repl-disable-tcp-nodelay': 'no',
    'slave-priority': '100',
    'no-appendfsync-on-rewrite': 'no',
    'slowlog-log-slower-than': '10000',
    'slowlog-max-len': '128',
    'latency-monitor-threshold': '0',
    'notify-keyspace-events': '""',
    'set-max-intset-entries': '512',
    'timeout': '0',
    'unixsocket': '/var/run/redislite/redis.socket',
    'unixsocketperm': '700',
    'zset-max-ziplist-entries': '128',
    'zset-max-ziplist-value': '64',
}


def settings(**kwargs):
    """
    Get config settings based on the defaults and the arguments passed

    Parameters
    ----------
    **kwargs
        Redis server arguments, the keyword is the setting, the value is the
        value.
        If the value is of type list, the setting will be  set multiple times
        once with each value.
        If the value is None, the setting will be removed from the default
        settings if it exists.

    Returns
    -------
    dict
        Dictionary containing redis server settings, with the key being the
        setting name.  The values are the settings.  If the value is a list
        the setting will be repeated with each specified value.
    """
    new_settings = copy(DEFAULT_REDIS_SETTINGS)
    new_settings.update(kwargs)

    return new_settings


def config_line(setting, value):
    """
    Generate a single configuration line based on the setting and value

    Parameters
    ----------
    setting : str
        The configuration setting

    value : str
        The value for the configuration setting

    Returns
    -------
    str
        The configuration line based on the setting and value
    """
    if setting in [
        'appendfilename', 'dbfilename', 'dbdir', 'dir', 'pidfile', 'unixsocket'
    ]:
        value = repr(value)
    return '{setting} {value}'.format(setting=setting, value=value)


def config(**kwargs):
    """
    Generate a redis configuration file based on the passed arguments

    Returns
    -------
    str
        Redis server configuration
    """
    # Get our settings
    config_dict = settings(**kwargs)
    config_dict['dir'] = config_dict['dbdir']
    del config_dict['dbdir']

    configuration = ''
    keys = list(config_dict.keys())
    keys.sort()
    for key in keys:
        if config_dict[key]:
            if isinstance(config_dict[key], list):
                for item in config_dict[key]:
                    configuration += config_line(
                        setting=key, value=item
                    ) + '\n'
            else:
                configuration += config_line(
                    setting=key, value=config_dict[key]
                ) + '\n'
        else:
            del config_dict[key]
    logger.debug('Using configuration: %s', configuration)
    return configuration
