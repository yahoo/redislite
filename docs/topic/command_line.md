Using the Redis Server directly
===============================
The `redis-server` application that is built by :mod:`redislite` during it's installation is installed into the
scripts directory during the installation.  This binary is a complete redis server and can be used independent of
the :mod:`redislite` module.

Since redis-lite installs an actual redis-server it is possible to use the :mod:`redislite` `redis-server` binary
directly and use more complex configurations than those created automatically by the :class:`redislite.Redis()` and
:class:`redislite.StrictRedis()` classes.

It is also possible to start the `redis-server` process with no arguments and use it with the unpatched :mod:`redis`
module.

See the `Redis documentation <http://redis.io/documentation>`_ for details about how to configure and run the
`redis-server` directly.