#!/usr/bin/env python
# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
from __future__ import print_function
import os
import json
import logging
from setuptools import setup
from setuptools.command.install import install
from distutils.command.build import build
from distutils.core import Extension
import distutils.util
from subprocess import call


logger = logging.getLogger(__name__)
METADATA_FILE = 'redislite/package_metadata.json'
BASEPATH = os.path.dirname(os.path.abspath(__file__))
REDIS_PATH = os.path.join(BASEPATH, 'redis.submodule')
revision = len(os.popen('git rev-list HEAD 2>/dev/null').readlines())
if revision > 0:
    # We're in a git repo, so not the installed package archive so we
    # want to generate a new package version
    if os.path.exists(METADATA_FILE):
        os.remove(METADATA_FILE)
if 'TRAVIS_BUILD_NUMBER' in os.environ.keys():
    revision = os.environ['TRAVIS_BUILD_NUMBER'].strip()
metadata = {
    'version': '1.0.%s' % revision
}


def readme():
    with open('README.md') as f:
        return f.read()


class build_redis(build):
    def run(self):
        # run original build code
        build.run(self)

        # build Redis
        logger.debug('Running build_redis')

        build_path = os.path.abspath(self.build_temp)

        os.environ['CC'] = 'gcc'
        os.environ['PREFIX'] = REDIS_PATH
        cmd = [
            'make',
            'MALLOC=libc',
            'V=' + str(self.verbose),
        ]

        #options = [
        #    'DEBUG=n',
        #]
        #cmd.extend(options)

        targets = ['install']
        cmd.extend(targets)

        target_files = [
            os.path.join(REDIS_PATH, 'bin/redis-server'),
            os.path.join(REDIS_PATH, 'bin/redis-cli'),
        ]

        def _compile():
            print('*' * 80)
            print(os.getcwd())
            call(cmd, cwd=REDIS_PATH)
            print('*' * 80)

        self.execute(_compile, [], 'compiling redis')

        # copy resulting tool to script folder
        self.mkpath(self.build_scripts)

        if not self.dry_run:
            for target in target_files:
                logger.debug('copy: %s -> %s', target, self.build_scripts)
                self.copy_file(target, self.build_scripts)


class InstallRedis(install):
    def initialize_options(self):
        install.initialize_options(self)
        self.build_scripts = None

    def finalize_options(self):
        install.finalize_options(self)
        self.set_undefined_options('build', ('build_scripts', 'build_scripts'))

    def run(self):
        # run original install code
        install.run(self)

        # install Redis executables
        logger.debug(
            'running InstallRedis %s -> %s', self.build_lib, self.install_lib
        )
        self.copy_tree(self.build_lib, self.install_lib)
        logger.debug(
            'running InstallRedis %s -> %s',
            self.build_scripts, self.install_scripts
        )
        self.copy_tree(self.build_scripts, self.install_scripts)


# Create a dictionary of our arguments, this way this script can be imported
#  without running setup() to allow external scripts to see the setup settings.
args = {
    'name': 'redislite',
    'version': metadata['version'],
    'author': 'Dwight Hubbard',
    'author_email': 'dhubbard@yahoo-inc.com',
    'url': 'https://github.com/yahoo/redislite',
    'license': 'License :: OSI Approved :: BSD License',
    'packages': ['redislite'],
    'description': 'Redis built into a python package',
    'install_requires': ['redis', 'psutil'],
    'long_description': readme(),
    'classifiers': [
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX :: BSD :: FreeBSD',
            'Operating System :: POSIX :: Linux',
            'Operating System :: POSIX :: SunOS/Solaris',
            'Operating System :: POSIX',
            'Programming Language :: C',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Libraries',
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities',
    ],
    'package_data': {
        'redislite': ['package_metadata.json']
    },
    'include_package_data': True,
    'cmdclass': {
        'build': build_redis,
        'install': InstallRedis,
    },

    # We put in a bogus extension module so wheel knows this package has
    # compiled components.
    'ext_modules': [
        Extension('dummy', sources=['src/dummy.c'])
    ],
    #'extras_require': {
    #    ':sys_platform=="darwin"': [],
    #    ':sys_platform=="linux"': [],
    #}
}
setup_arguments = args

# Add any scripts we want to package
if os.path.isdir('scripts'):
    setup_arguments['scripts'] = [
        os.path.join('scripts', f) for f in os.listdir('scripts')
    ]


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    logger.debug('Building for platform: %s', distutils.util.get_platform())
    # We're being run from the command line so call setup with our arguments

    if os.path.isfile(METADATA_FILE):
        metadata = json.load(open(METADATA_FILE))
    else:
        json.dump(metadata, open(METADATA_FILE, 'w'))
    setup(**setup_arguments)
