# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
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
