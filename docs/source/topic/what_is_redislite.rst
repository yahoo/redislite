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


Backwards Compatibility
-----------------------

To provide compatibility with existing python code that uses the redis bindings.
Redislite provides functions to patch the :mod:`redis` module to use the
:mod:`redislite` module.  This allows most existing code that uses redis to
use the redislite features.