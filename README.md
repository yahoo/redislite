# Redislite

[![CI/CD](https://img.shields.io/badge/CI/CD-Screwdriver-blue.svg)](https://screwdriver.cd/)
[![Build Status](https://cd.screwdriver.cd/pipelines/2880/badge)](https://cd.screwdriver.cd/pipelines/2880)
[![Codestyle](https://img.shields.io/badge/code%20style-pep8-blue.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Coverage](https://codecov.io/gh/yahoo/redislite/branch/master/graph/badge.svg)](https://codecov.io/gh/yahoo/redislite)
[![Current Version](https://img.shields.io/pypi/v/redislite.svg)](https://pypi.python.org/pypi/redislite/)
[![Supported Python](https://img.shields.io/badge/python-3.6,3.7,3.8-blue.svg)](https://pypi.python.org/pypi/redislite/)
[![License](https://img.shields.io/pypi/l/redislite.svg)](https://pypi.python.org/pypi/redislite/)
[![Documentation](https://readthedocs.org/projects/redislite/badge/?version=latest)](http://redislite.readthedocs.org/en/latest/)


## Description

Redislite is a self contained Python interface to the Redis key-value store.

It provides enhanced versions of the Redis-Py Python bindings for Redis.  That provide the following added functionality:

* **Easy to use** - It provides a built in Redis server that is automatically installed, configured and managed when the Redis bindings are used.
* **Flexible** - Create a single server shared by multiple programs or multiple independent servers.  All the servers provided by Redislite support all Redis functionality including advanced features such as replication and clustering.
* **Compatible** - It provides enhanced versions of the Redis-Py python Redis bindings as well as functions to patch them to allow most existing code that uses them to run with little or no modifications.
* **Secure** - It uses a secure default Redis configuraton that is only accessible by the creating user on the computer system it is run on.

## Requirements

The redislite module requires Python 3.6 or higher.


### Installing requirements on Linux

Make sure Python development headers are available when installing redislite.

On Ubuntu/Debian systems, install them with:

`apt-get install python-dev`

On Redhat/Fedora systems, install them with:

`yum install python-devel`

### Installing requirements on Mac OSX

Redislite for OSX comes as a wheel package by default that can be installed
using current versions of pip.

To install Redislite on MacOSX using the sdist package instead you will need
the XCode command line utilities installed.  If you do not have xcode
installed on recent OSX releases they can be installed by
running:

`xcode-select --install`

### Installing requirements on Microsoft Windows

Redislite can be installed on newer releases of Windows 10 under the Bash on Ubuntu shell.

Install it using the instructions at https://msdn.microsoft.com/commandline/wsl/install_guide 

Then start the bash shell and install the python-dev package as follows:

`apt-get install python-dev`    
    
## Installation

To install redislite, simply:

```console
$ pip install redislite
```

or from source:

```console
$ python setup.py install
```


## Getting Started

redislite provides enhanced versions of the redis-py redis.Redis() and 
redis.StrictRedis() classes that take the same arguments as the corresponding
redis classes and take one additional optional argument.  Which is the
name of the Redis rdb file to use.  If the argument is not provided it will
create set up a new redis server.

redislite also provides functions to MonkeyPatch the redis.Redis and 
redis.StrictRedis classes to use redislite, so existing python code that uses
Redis can use the redislite version.
    
## Examples

Here are some examples of using the redislite module.

### Setting a value

Here we open a Python shell and set a key in our embedded Redis db.  Redislite will automatically start the Redis server when
the Redis() object is created and shut it down cleanly when the Python interpreter exits.

```python
>>> from redislite import Redis
>>> redis_connection = Redis('/tmp/redis.db')
>>> redis_connection.keys()
[]
>>> redis_connection.set('key', 'value')
True
>>> redis_connection.get('key')
'value'
```

### Persistence

Now we open the same Redis db and access the key we created during the last run.  Redislite will automatically start the
Redis server using the same configuration as last time, so the value that was set in the previous example is still available.

```python
>>> from redislite import Redis
>>> redis_connection = Redis('/tmp/redis.db')
>>> redis_connection.keys()
['key']
>>> redis_connection.get('key')
'value'
```

## Compatibility

It's possible to MonkeyPatch the normal Redis classes to allow modules 
that use Redis to use the redislite classes.  Here we patch Redis and use the 
redis_collections module.

```python
>>> import redislite.patch
>>> redislite.patch.patch_redis()
>>> import redis_collections
>>> td = redis_collections.Dict()
>>> td['foo']='bar'
>>> td.keys()
['foo']
```

## Running and using Multiple servers

Redislite will start a new server if the redis rdb fileame isn't specified or is new.  In this example we start 10 seperate redis servers and set the value of the key 'servernumber' to a different value in each server.  

Then we access the value of 'servernumber' and print it.

```python
>>> import redislite
>>> servers = {}
>>> for redis_server_number in range(10):
...     servers[redis_server_number] = redislite.Redis()
...     servers[redis_server_number].set('servernumber', redis_server_number)
...
True
True
True
True
True
True
True
True
True
True
>>> for redis_server in servers.values():
...     redis_server.get('servernumber')
...
b'0'
b'1'
b'2'
b'3'
b'4'
b'5'
b'6'
b'7'
b'8'
b'9'
```

## Multiple Servers with different configurations in the same script

It's possible to spin up multiple instances with different
configuration settings for the Redis server.  Here is an example that sets up 2
redis server instances.  One instance is configured to listen on port 8002, the
second instance is a read-only slave of the first instance.


```python
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
```

## More Information

There is more detailed information on the redislite documentation page at
http://redislite.readthedocs.org/en/latest/

Redislite is Free software under the New BSD license, see LICENSE.txt for
details.
