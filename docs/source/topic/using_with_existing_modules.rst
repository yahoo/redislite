
Using redislite with existing python code
=========================================

The redislite patch functionality can be used to make many existing python
modules that use redis to work with minimal modifications.

redis-collections
-----------------
Here is how to patch the redis_collections module to use redislite

.. code-block:: python

    >>> import redislite.patch
    >>> redislite.patch.patch_redis()
    >>> import redis_collections
    >>> td = redis_collections.Dict()
    >>> td['foo']='bar'
    >>> td.keys()
    ['foo']


Walrus
------
First, install both walrus and redislite.

Install both modules::

    $ pip install walrus redislite


Then patch redis before using walrus.  Optionally specifying a redis db if
the result needs to be usable after the script finishes running.

.. code-block:: python

    >>> from redislite.patch import patch_redis
    >>> patch_redis('/tmp/walrus.db')
    >>> from walrus import *
    >>> db = Database()
    >>> huey = db.Hash('huey')
    >>> huey.update(color='white', temperament='ornery', type='kitty')
    <Hash "huey": {'color': 'white', 'type': 'kitty', 'temperament': 'ornery'}>
    >>> huey.keys()
    ['color', 'type', 'temperament']
    >>> 'color' in huey
    True
    >>> huey['color']
    'white'