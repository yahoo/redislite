redislite
*********

.. image:: https://img.shields.io/travis/yahoo/redislite.svg
    :target: https://travis-ci.org/yahoo/redislite
    
.. image:: https://img.shields.io/coveralls/yahoo/redislite.svg
  :target: https://coveralls.io/r/yahoo/redislite

.. image:: https://img.shields.io/pypi/dm/redislite.svg
    :target: https://pypi.python.org/pypi/redislite/

.. image:: https://img.shields.io/pypi/v/redislite.svg
    :target: https://pypi.python.org/pypi/redislite/

.. image:: https://img.shields.io/badge/python-2.7,3.4,pypy-blue.svg
    :target: https://pypi.python.org/pypi/redislite/

.. image:: https://img.shields.io/pypi/l/redislite.svg
    :target: https://pypi.python.org/pypi/redislite/

---------------------------------------------------------------------

.. image:: https://readthedocs.org/projects/redislite/badge/?version=latest
    :target: http://redislite.readthedocs.org/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/IRC-redislite-blue.svg
    :target: http://webchat.freenode.net/?channels=%23redislite&uio=d4
    :alt: IRC

.. image:: https://img.shields.io/badge/Group-pythonredislite-blue.svg
    :target: https://groups.yahoo.com/neo/groups/pythonredislite/info
    :alt: Yahoo Group pythonredislite



Description
===========
Self contained Python interface to the Redis key-value store.

It makes it possible to use Redis securely without the need to install and
configure a redis server.


Requirements
------------
The redislite module requires Python 2.7 or higher.

Installing on Linux
~~~~~~~~~~~~~~~~~~~

Make sure Python development headers are available when installing redislite.

On Ubuntu/Debian systems, install them with:

.. code-block::

    apt-get install python-dev

On Redhat/Fedora systems, install them with:

.. code-block::

    yum install python-devel

Installing on Mac OSX
~~~~~~~~~~~~~~~~~~~~~

Redislite for OSX comes as a wheel package by default that can be installed
using current versions of pip.

To install Redislite on MacOSX using the sdist package instead you may need
the XCode command line utilities installed.  If you do not have xcode
installed on recent OSX releases they can be installed by
running::

    xcode-select --install

Note redislite and its dependencies use the gcc compiler. On OSX you may run
into errors indicating that your machine is using clang to compile instead, for
example::

    clang: error: unknown argument: '-mno-fused-madd' [-Wunused-command-line-argument-hard-error-in-future]

If this is the case, set your environment variable to override the use of clang
in favor of gcc::

    CC=gcc


Installation
============

To install redislite, simply:

.. code-block::

    $ pip install redislite

or using easy_install:

.. code-block::

    $ easy_install redislite

or from source:

.. code-block::

    $ python setup.py install


Getting Started
===============

.. code-block:: python

    >>> import redislite
    >>> r = redislite.StrictRedis()
    >>> r.set('foo', 'bar')
    True
    >>> r.get('foo')
    'bar'

Usage
=====

redislite provides enhanced versions of the redis.Redis() and 
redis.StrictRedis() classes that  take the same arguments as the corresponding
redis classes and take one additional optional argument.  Which is the
name of the Redis rdb file to use.  If the argument is not provided it will
create a new one.

redislite also provides functions to MonkeyPatch the redis.Redis and 
redis.StrictRedis classes to use redislite, so existing python code that uses
Redis can use the redislite version.
    
Example
=======

Here we open a Python shell and set a key in our embedded Redis db

.. code-block:: python

    >>> from redislite import Redis
    >>> redis_connection = Redis('/tmp/redis.db')
    >>> redis_connection.keys()
    []
    >>> redis_connection.set('key', 'value')
    True
    >>> redis_connection.get('key')
    'value'

Here we open the same Redis db and access the key we created during the last
run

.. code-block:: python

    >>> from redislite import Redis
    >>> redis_connection = Redis('/tmp/redis.db')
    >>> redis_connection.keys()
    ['key']
    >>> redis_connection.get('key')
    'value'

It's also possible to MonkeyPatch the normal Redis classes to allow modules 
that use Redis to use the redislite classes.  Here we patch Redis and use the 
redis_collections module.

.. code-block:: python

    >>> import redislite.patch
    >>> redislite.patch.patch_redis()
    >>> import redis_collections
    >>> td = redis_collections.Dict()
    >>> td['foo']='bar'
    >>> td.keys()
    ['foo']

Finally it's possible ot spin up multiple instances with different
configuration values for the Redis server.  Here is an example that sets up 2
redis instances.  One instance is configured to listen on port 8002, the
second instance is a read-only slave of the first instance.


.. code-block:: python

    Python 2.7.6 (default, Mar 22 2014, 22:59:56)
    [GCC 4.8.2] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import redislite
    >>> master=redislite.Redis(serverconfig={'port': '8002'})
    >>> slave=redislite.Redis(serverconfig={'slaveof': "127.0.0.1 8002"})
    >>> slave.keys()
    []
    >>> master.set('key', 'value')
    True
    >>> master.keys()
    ['key']
    >>> slave.keys()
    ['key']
    >>>

More Information
================

There is more detailed information on the redislite documentation page at
http://redislite.readthedocs.org/en/latest/

Redislite is Free software under the New BSD license, see LICENSE.txt for
details.
