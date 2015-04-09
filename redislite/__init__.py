# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
This module provides access to a redis server using a redis server embedded
in the module.  It provides enhanced redis bindings that are able to configure
run, and cleanup a redis server when they are accessed.

Example:
  To access redis using a newly installed and configured redis server, then
  set and retrieve some data:

      >>> import redislite
      >>> connection = redislite.Redis()
      >>> connection.set('key', 'value')
      True
      >>> connection.get('key')
      'value'
      >>>
"""
import json
import os


_metadata_file = os.path.join(
    os.path.dirname(__file__),
    'package_metadata.json'
)

if os.path.exists(_metadata_file):
    with open(_metadata_file) as fh:
        _package_metadata = json.load(fh)
        __version__ = str(_package_metadata['version'])
        __git_version__ =  str(_package_metadata['git_version'])
        __git_origin__ = str(_package_metadata['git_origin'])
        __git_branch__ = str(_package_metadata['git_branch'])
        __git_hash__ = str(_package_metadata['git_hash'])
else:   # pragma: no cover
    __version__ = str('0.0.0')
    __git_version__ = str("")
    __git_origin__ = str("")
    __git_branch__ = str("")
    __git_hash__ = str("")


__all__ = ['client', 'configuration', 'patch']

from .client import Redis, StrictRedis  # NOQA
