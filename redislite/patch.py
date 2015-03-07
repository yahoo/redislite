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
    Monkeypatch the redis.Redis() class
    :return:
    """
    global original_classes
    global Redis_Patched

    if Redis_Patched:
        logger.info('redis.Redis class has already been patched.')
        return

    if dbfile:
        Redis.dbdir = os.path.dirname(dbfile)
        Redis.dbfilename = os.path.basename(dbfile)
        Redis.settingregistryfile = os.path.join(
                Redis.dbdir, Redis.dbfilename + '.settings'
            )

    original_classes['Redis'] = redis.Redis
    redis.Redis = Redis
    Redis_Patched = True


def unpatch_redis_Redis():
    global original_classes
    global Redis_Patched

    if original_classes['Redis']:    # pragma: no cover
        redis.Redis = original_classes['Redis']
        original_classes['Redis'] = None
    Redis_Patched = False


def patch_redis_StrictRedis(dbfile=None):
    """
    Monkeypatch the redis.StrictRedis() class
    :return:
    """
    global original_classes
    global StrictRedis_Patched

    if StrictRedis_Patched:
        logger.info('redis.StrictRedis class has already been patched')
        return

    if dbfile:
        StrictRedis.dbdir = os.path.dirname(dbfile)
        StrictRedis.dbfilename = os.path.basename(dbfile)
        StrictRedis.settingregistryfile = os.path.join(
                StrictRedis.dbdir, StrictRedis.dbfilename + '.settings'
            )

    original_classes['StrictRedis'] = redis.StrictRedis
    redis.StrictRedis = StrictRedis
    StrictRedis_Patched = True


def unpatch_redis_StrictRedis():
    global original_classes
    global StrictRedis_Patched

    if original_classes['StrictRedis']:   # pragma: no cover
        redis.StrictRedis = original_classes['StrictRedis']
        original_classes['StrictRedis'] = None
    StrictRedis_Patched = False


def patch_redis(dbfile=None):
    """
    Monkeypatch all the redis classes provided by redislite
    :return:
    """
    for patch in [patch_redis_Redis, patch_redis_StrictRedis]:
        patch(dbfile)


def unpatch_redis():
    """
    Un-Monkeypatch all the redis classes provided by redislite
    :return:
    """
    for unpatch in [unpatch_redis_Redis, unpatch_redis_StrictRedis]:
        unpatch()
