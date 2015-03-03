# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
Functions to replace (monkeypatch) the redis module classes
with redislite classes.
"""
import collections
import redis
from .client import Redis, StrictRedis

original_classes = collections.defaultdict(lambda: None)  # pragma: no cover


def patch_redis_Redis():
    """
    Monkeypatch the redis.Redis() class
    :return:
    """
    global original_classes

    original_classes['Redis'] = redis.Redis
    redis.Redis = Redis


def unpatch_redis_Redis():
    global original_classes

    if original_classes['Redis']:    # pragma: no cover
        redis.Redis = original_classes['Redis']
        original_classes['Redis'] = None


def patch_redis_StrictRedis():
    """
    Monkeypatch the redis.StrictRedis() class
    :return:
    """
    global original_classes

    original_classes['StrictRedis'] = redis.StrictRedis
    redis.StrictRedis = StrictRedis


def unpatch_redis_StrictRedis():
    global original_classes

    if original_classes['StrictRedis']:   # pragma: no cover
        redis.StrictRedis = original_classes['StrictRedis']
        original_classes['StrictRedis'] = None


def patch_redis():
    """
    Monkeypatch all the redis classes provided by redislite
    :return:
    """
    for patch in [patch_redis_Redis, patch_redis_StrictRedis]:
        patch()


def unpatch_redis():
    """
    Un-Monkeypatch all the redis classes provided by redislite
    :return:
    """
    for unpatch in [unpatch_redis_Redis, unpatch_redis_StrictRedis]:
        unpatch()
