# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
Functions to replace (monkeypatch) the redis module classes
with redislite classes.
"""
import collections
import logging
import os
import redis
from .client import Redis, StrictRedis


logger = logging.getLogger(__name__)


original_classes = collections.defaultdict(lambda: None)  # pragma: no cover
Redis_Patched = False
StrictRedis_Patched = False


def patch_redis_Redis(dbfile=None):
    """
    This class patches the redis module to replace the :class:`redis.Redis()`
    class with the redislite enhanced :class:`redislite.Redis()` class that uses
    the embedded redis server.


    Example:
        patch_redis_Redis('/tmp/redis.db')


    Notes:
        If the dbfile parameter is not passed, each instance of the
        redis.Redis() class with no arguments will get a separate redis
        server.  If the dbfile parameter is provided, all instances of
        the redis.Redis() class without a host or path argument will
        share/reference the same redis server.

    Args:
        dbfile(str):
            The name of the Redis db file to be used.  If this argument is
            passed all instances of the :class:`redis.Redis` class will share a
            single embedded redis server.

    Returns:
        This function does not return any values.
    """
    global original_classes
    global Redis_Patched

    if Redis_Patched:
        logger.info('redis.Redis class has already been patched.')
        return

    if dbfile:
        if dbfile == os.path.basename(dbfile):
            dbfile = os.path.join(os.getcwd(), dbfile)
        Redis.dbdir = os.path.dirname(dbfile)
        Redis.dbfilename = os.path.basename(dbfile)
        Redis.settingregistryfile = os.path.join(
            Redis.dbdir, Redis.dbfilename + '.settings'
        )

    original_classes['Redis'] = redis.Redis
    redis.Redis = Redis
    Redis_Patched = True


def unpatch_redis_Redis():
    """
    This class unpatches the :class:`redis.Redis()` class of the redis module
    and restores the original :class:`redis.Redis()`  class.


    Example:
        unpatch_redis_Redis()


    Returns:
        This function does not return any values.
    """
    global original_classes
    global Redis_Patched

    if original_classes['Redis']:    # pragma: no cover
        redis.Redis = original_classes['Redis']
        original_classes['Redis'] = None
    Redis_Patched = False


def patch_redis_StrictRedis(dbfile=None):
    """
    This class patches the redis module to replace the
    :param dbfile:
    :class:`redis.StrictRedis()` class with the redislite enhanced
    :class:`redislite.StrictRedis()` class that uses the embedded redis server.


    Example:
        patch_redis_StrictRedis('/tmp/redis.db')


    Notes:
        If the dbfile parameter is not passed, all :class:`redis.StrictRedis()`
        class with no arguments will get a separate redis server.  If the
        dbfile parameter is provided, all instances of the
        :class:`redis.Redis()` class passed with the same dbfile value
        will share/reference the same redis server.

    Args:
        dbfile(str):
            The name of the Redis db file to be used.  If this argument is passed all instances of the
            :class:`redis.Redis` class will share a single instance of the embedded redis server.

    Returns:
        This function does not return any values.
    """
    global original_classes
    global StrictRedis_Patched

    if StrictRedis_Patched:
        logger.info('redis.StrictRedis class has already been patched')
        return

    if dbfile:
        if dbfile == os.path.basename(dbfile):
            dbfile = os.path.join(os.getcwd(), dbfile)
        StrictRedis.dbdir = os.path.dirname(dbfile)
        StrictRedis.dbfilename = os.path.basename(dbfile)
        StrictRedis.settingregistryfile = os.path.join(
            StrictRedis.dbdir, StrictRedis.dbfilename + '.settings'
        )

    original_classes['StrictRedis'] = redis.StrictRedis
    redis.StrictRedis = StrictRedis
    StrictRedis_Patched = True


def unpatch_redis_StrictRedis():
    """
    This class unpatches the :class:`redis.StrictRedis()` class of the redis
    module and restores the original :class:`redis.StrictRedis()`  class.


    Example:
        unpatch_redis_StrictRedis()


    Returns:
        This function does not return any values.
    """
    global original_classes
    global StrictRedis_Patched

    if original_classes['StrictRedis']:   # pragma: no cover
        redis.StrictRedis = original_classes['StrictRedis']
        original_classes['StrictRedis'] = None
    StrictRedis_Patched = False


def patch_redis(dbfile=None):
    """
    Patch all the redis classes provided by redislite that have been patched.


    Example:
        patch_redis('/tmp/redis.db')


    Notes:
        If the dbfile parameter is not passed, each any instances of :class:`redis.StrictRedis()` class with no
        arguments will get a unique instance of the redis server.  If the dbfile parameter is provided, all instances
        of :class:`redis.Redis()` will share/reference the same instance of the redis server.

    Args:
        dbfile(str):
            The name of the Redis db file to be used.  If this argument is passed all instances of the
            :class:`redis.Redis()` class will share a single instance of the embedded redis server.

    Returns:
        This function does not return any values.
    """
    for patch in [patch_redis_Redis, patch_redis_StrictRedis]:
        patch(dbfile)


def unpatch_redis():
    """
    Unpatch all the redis classes provided by :mod:`redislite` that have been patched.

    Example:
        unpatch_redis()
    """
    for unpatch in [unpatch_redis_Redis, unpatch_redis_StrictRedis]:
        unpatch()
