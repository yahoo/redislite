# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
Redislite Debug Utilities

This module contains utility functions useful for troubleshooting redislite.

This module can be run from the command line using the following command::

    python -m redislite.debug


This will output information like the following::

    $ python -m redislite.debug
    Redislite debug information:
        Version: 1.0.171
        Module Path: /tmp/redislite/lib/python3.4/site-packages/redislite

        Installed Redis Server:
            Redis Executable: /tmp/redislite/lib/python3.4/site-packages/redislite/bin/redis-server
            build = 3a2b5dab9c14cd5e
            sha = 4657e47d:1
            bits = 64
            v = 2.8.17
            malloc = libc

        Found redis-server: /tmp/redislite/lib/python3.4/site-packages/redislite/bin/redis-server
            v = 2.8.17
            sha = 4657e47d:1
            malloc = libc
            bits = 64
            build = 3a2b5dab9c14cd5e

        Source Code Information
            Git Source URL: https://github.com/yahoo/redislite/tree/2ebd1b4d9c9ad41c78e8048fda3c69d2917c0348
            Git Hash: 2ebd1b4d9c9ad41c78e8048fda3c69d2917c0348
            Git Version: 1.0.171
            Git Origin: https://github.com/yahoo/redislite.git
            Git Branch: master


When run from the command line this will print a dump of information about
the module and it's build information.
"""
from __future__ import print_function
from distutils.spawn import find_executable
from .__init__ import __version__, __git_version__, __source_url__, \
    __git_hash__, __git_origin__, __git_branch__, __redis_server_info__, \
    __redis_executable__
import os


def print_debug_info():
    """
    Display information about the redislite build, and redis-server on stdout.
    :return:
    """
    redis_server = find_executable('redis-server')
    if __redis_executable__:  # pragma: no cover
        redis_server = __redis_executable__
    print("Redislite debug information:")
    print('\tVersion: %s' % __version__)
    print('\tModule Path: %s' % os.path.dirname(__file__))
    print('\n\tInstalled Redis Server:')
    print('\t\tRedis Executable: %s' % redis_server)
    for key, value in __redis_server_info__.items():  # pragma: no cover
        print('\t\t%s = %s' % (key, value))
    print('\n\tFound redis-server: %s' % redis_server)
    for item in os.popen('%s --version' % redis_server).read().strip().split():
        if '=' in item:
            key, value = item.split('=')
            print('\t\t%s = %s' % (key, value))
    print('')
    print('\tSource Code Information')
    if __git_version__:  # pragma: no cover
        print('\t\tGit Source URL: %s' % __source_url__)
        print('\t\tGit Hash: %s' % __git_hash__)
        print('\t\tGit Version: %s' % __git_version__)
        print('\t\tGit Origin: %s' % __git_origin__)
        print('\t\tGit Branch: %s' % __git_branch__)


if __name__ == '__main__':  # pragma: no cover
    print_debug_info()
