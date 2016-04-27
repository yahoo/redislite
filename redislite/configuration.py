# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
This module contains functions to generate a redis configuration from a
configuration template.
"""
import logging
from copy import copy


logger = logging.getLogger(__name__)


DEFAULT_REDIS_SETTINGS = {
    'activerehashing': 'yes',
    'aof-rewrite-incremental-fsync': 'yes',
    'appendonly': 'no',
    'appendfilename': '"appendonly.aof"',
    'appendfsync': 'everysec',
    'auto-aof-rewrite-percentage': '100',
    'auto-aof-rewrite-min-size': '64mb',
    'bind': None,
    'daemonize': 'yes',
    'databases': '16',
    'dbdir': './',
    'dbfilename': 'redis.db',
    'pidfile': '/var/run/redislite/redis.pid',
    'port': '0',
    'save': ['900 1', '300 100', '60 200', '15 1000'],
    'tcp-backlog': '511',
    'unixsocket': '/var/run/redislite/redis.socket',
    'unixsocketperm': '700',
    'tcp-keepalive': '0',
    'loglevel': 'notice',
    'logfile' : 'redis.log',
    'stop-writes-on-bgsave-error': 'yes',
    'rdbcompression': 'yes',
    'rdbchecksum': 'yes',
    'timeout': '0',
    'slave-serve-stale-data': 'yes',
    'slave-read-only': 'yes',
    'repl-disable-tcp-nodelay': 'no',
    'slave-priority': '100',
    'no-appendfsync-on-rewrite': 'no',
    'aof-load-truncated': 'yes',
    'lua-time-limit': '5000',
    'slowlog-log-slower-than': '10000',
    'slowlog-max-len': '128',
    'latency-monitor-threshold': '0',
    'notify-keyspace-events': '""',
    'hash-max-ziplist-entries': '512',
    'hash-max-ziplist-value': '64',
    'list-max-ziplist-entries': '512',
    'list-max-ziplist-value': '64',
    'set-max-intset-entries': '512',
    'zset-max-ziplist-entries': '128',
    'zset-max-ziplist-value': '64',
    'hll-sparse-max-bytes': '3000',
    'hz': '10',
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
                    configuration += '{key} {value}\n'.format(
                        key=key, value=item
                    )
            else:
                configuration += '{key} {value}\n'.format(
                    key=key, value=config_dict[key]
                )
        else:
            del config_dict[key]
    logger.debug('Using configuration: %s', configuration)
    return configuration
