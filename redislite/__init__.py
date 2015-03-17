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

if os.path.exists(_metadata_file):  # pragma: no cover
    with open(_metadata_file) as fh:
        _package_metadata = json.load(fh)
        __version__ = _package_metadata['version']
else:
    __version__ = '0.0.0'  # pragma: no cover


__all__ = ['client', 'configuration', 'patch']

from .client import Redis, StrictRedis  # NOQA
