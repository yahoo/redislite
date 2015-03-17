How redislite works
===================

:mod:`redislite` provides enhanced versions of the :class:`redis.Redis()` and
:class:`redis.StrictRedis()` classes.

These enhanced classes accept the same arguments as the corresponding redis
classes.

Both enhanced classes accept one additional optional argument, which is the
filename to use for the redis.db file.

These enhanced classes provide the following additional functionality:

* They configure and start and embedded copy of the redis server running on a unix domain socket in the redislist temp directory for the communication to the redis service.
* TCP communication is disabled.
* The classes have two additional attributes:
    * db - The path to the db backing file for the redis instance.
    * pid - The process id (pid) of the embedded redis server.
* If the db argument is passed and there is another redislite object using that db, it will create a new connection to that redislite instance.
* The redis server for a redislite object is shutdown and it's configuration is deleted when the object is cleaned up.
