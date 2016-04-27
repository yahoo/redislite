What is redislite
=================

The :mod:`redislite` module contains a complete redis server along with enhanced redis bindings
that automatically set up and run the embedded redis server when accessed and
shutdown and cleanup the redis server when python exits.


Enhanced Redis Bindings
-----------------------

The enhanced redis bindings include extended versions of the
:class:`redis.Redis()` and :class:`redis.StrictRedis()` classes.  It also
contains functions to patch the redis module to use these new extended classes.


Secure By Default
-----------------

Redislite defaults to a redis server configuration that is more secure than
the default configuration for the redis server.  This is due to the following
differences:

* Redislite defaults to using unix domain sockets for the redis connection.  So
  the server is not accessible over the computer network by default.

* Redislite locks down the permissions of the unix domain sockets used to only
  allow the creating user access.


Backwards Compatibility
-----------------------

To provide compatibility with existing python code that uses the redis bindings.
Redislite provides functions to patch the :mod:`redis` module to use the
:mod:`redislite` module.  This allows most existing code that uses redis to
use the redislite features.