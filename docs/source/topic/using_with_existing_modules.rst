
Using redislite with existing python code
=========================================

The redislite patch functionality can be used to make many existing python
modules that use redis to work with minimal modifications.

Celery
------
.. code-block:: python

    # settings.py

    from redislite import Redis

    # Create a Redis instance using redislite
    REDIS_DB_PATH = os.path.join('/tmp/my_redis.db')
    rdb = Redis(RDB_PATH)
    REDIS_SOCKET_PATH = 'redis+socket://%s' % (rdb.socket_file, )

    # Use redislite for the Celery broker
    BROKER_URL = REDIS_SOCKET_PATH

    # (Optionally) use redislite for the Celery result backend
    CELERY_RESULT_BACKEND = REDIS_SOCKET_PATH

.. code-block:: python

    # your_celery_app.py

    from celery import Celery

    # for django projects
    from django.conf import settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    celery_app = Celery('my_app')
    celery_app.config_from_object('django.conf:settings')

    # for other projects
    celery_app = Celery('my_app')
    celery_app.config_from_object('settings')

Note that only one Redis instance is created, and others merely discover the running instance and use its existing socket file path.

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


RQ
--
When using rq you will need to specify a db_filename for the connection.

To put jobs on queues, you don't have to do anything special, just define your typically lengthy or blocking function:

.. code-block:: python

    import requests

    def count_words_at_url(url):
        resp = requests.get(url)
        return len(resp.text.split())

Then, create a RQ queue:

.. code-block:: python

    from redislite import Redis
    from rq import Queue

    q = Queue(connection=Redis('RQ_example.rdb'))

    And enqueue the function call:

    from my_module import count_words_at_url
    result = q.enqueue(
                 count_words_at_url, 'http://nvie.com')

For a more complete example, refer to the docs. But this is the essence.
The worker

To start executing enqueued function calls in the background, start a worker from your project's directory:

.. code-block::

    $ rqworker
    *** Listening for work on default
    Got count_words_at_url('http://nvie.com') from default
    Job result = 818
    *** Listening for work on default


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
