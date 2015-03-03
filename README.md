===============================
redislite
===============================

Description
-----------
Redis made simple.  This module makes using Redis simple. 

The module contains an embedded redis server that it will automatically 
configure and start when the redis bindings are accessed. 

It kills the embedded redis server and cleans up when the redislite object is
deleted or the python interpreter exists.

It also provides functions to patch the normal redis bindings module to use the
redislite module so existing code that uses the redis bindings can be used 
without modification.

Usage
-----
redislite provides enhanced versions of the redis.Redis() and redis.StrictRedis() classes.

These enhanced classes take the same arguments as they're corresponding redis classes.

Both enhanced classes accept one additional optional argument, which is the filename to use for the redis.db file.

These enhanced classes provide the following additional functionality:

* They configure and start and embedded copy of the redis server running on a unix domain socket in the redislist temp directory for the communication to the redis service.
* TCP communication is disabled.
* The classes have two additional attributes:
    * db - The path to the db backing file for the redis instance.
    * pid - The process id (pid) of the embedded redis server.
* If the db argument is passed and there is another redislite object using that db, it will create a new connection to that redislite instance.
* The redis server for a redislite object is shutdown and it's configuration is deleted when the object is cleaned up.
    
redislite also provides functions to MonkeyPatch the redis.Redis and redis.StrictRedis classes to use redislite.
    
Example
-------

Here we open a python shell and set a key in our embedded redis db

    $ python
    Python 2.7.5 (default, Mar  9 2014, 22:15:05)
    [GCC 4.2.1 Compatible Apple LLVM 5.0 (clang-500.0.68)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from redislite import Redis
    >>> redis_connection = Redis('/tmp/redis.db')
    >>> redis_connection.keys()
    []
    >>> redis_connection.set('key', 'value')
    True
    >>> redis_connection.get('key')
    'value'
    >>> quit()
    $

Here we open the same redis db and access the key we created during the last run

    (testvenv)airreport-lm:redislite dhubbard$ python
    Python 2.7.5 (default, Mar  9 2014, 22:15:05)
    [GCC 4.2.1 Compatible Apple LLVM 5.0 (clang-500.0.68)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from redislite import Redis
    >>> redis_connection = Redis('/tmp/redis.db')
    >>> redis_connection.keys()
    ['key']
    >>> redis_connection.get('key')
    'value'
    >>> quit()
    $

It's also possible to MonkeyPatch the normal redis classes to allow modules that use redis to use the redislite classes.  Here we patch redis and use the redis_collections module.

    (py27)airreport-lm:redislite dhubbard$ python
    Python 2.7.5 (default, Mar  9 2014, 22:15:05)
    [GCC 4.2.1 Compatible Apple LLVM 5.0 (clang-500.0.68)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import redislite.patch
    >>> redislite.patch.patch_redis()
    >>> import redis_collections
    >>> td = redis_collections.Dict()
    >>> td['foo']='bar'
    >>> td.keys()
    ['foo']
    >>> quit()
    $
