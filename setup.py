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
METADATA_FILENAME = 'redislite/package_metadata.json'
BASEPATH = os.path.dirname(os.path.abspath(__file__))
REDIS_PATH = os.path.join(BASEPATH, 'redis.submodule')


def readme():
    with open('README.rst') as f:
        return f.read()


class build_redis(build):
    def run(self):
        # run original build code
        build.run(self)

        # build Redis
        logger.debug('Running build_redis')

        os.environ['CC'] = 'gcc'
        os.environ['PREFIX'] = REDIS_PATH
        cmd = [
            'make',
            'MALLOC=libc',
            'V=' + str(self.verbose),
        ]

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
    'version': '1.0.62',
    'author': 'Dwight Hubbard',
    'author_email': 'dhubbard@yahoo-inc.com',
    'url': 'https://github.com/yahoo/redislite',
    'license': 'BSD',
    'packages': ['redislite'],
    'description': 'Redis built into a python package',
    'install_requires': ['redis', 'psutil'],
    'requires': ['redis', 'psutil'],
    'long_description': readme(),
    'classifiers': [
            'Development Status :: 4 - Beta',
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
            'Programming Language :: Python :: Implementation :: PyPy',
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
    # 'extras_require': {
    #     ':sys_platform=="darwin"': [],
    #     ':sys_platform=="linux"': [],
    # }
}
setup_arguments = args

# Add any scripts we want to package
if os.path.isdir('scripts'):
    setup_arguments['scripts'] = [
        os.path.join('scripts', f) for f in os.listdir('scripts')
    ]


class Git(object):
    version_list = ['0', '7', '0']

    def __init__(self, version=None):
        if version:
            self.version_list = version.split('.')

    @property
    def version(self):
        """
        Generate a Unique version value from the git information
        :return:
        """
        git_rev = len(os.popen('git rev-list HEAD').readlines())
        if git_rev != 0:
            self.version_list[-1] = '%d' % git_rev
        version = '.'.join(self.version_list)
        return version

    @property
    def branch(self):
        """
        Get the current git branch
        :return:
        """
        return os.popen('git rev-parse --abbrev-ref HEAD').read().strip()

    @property
    def hash(self):
        """
        Return the git hash for the current build
        :return:
        """
        return os.popen('git rev-parse HEAD').read().strip()

    @property
    def origin(self):
        """
        Return the fetch url for the git origin
        :return:
        """
        for item in os.popen('git remote -v'):
            split_item = item.strip().split()
            if split_item[0] == 'origin' and split_item[-1] == '(push)':
                return split_item[1]


def get_and_update_metadata():
    """
    Get the package metadata or generate it if missing
    :return:
    """
    if not os.path.exists('.git') and os.path.exists(METADATA_FILENAME):
        with open(METADATA_FILENAME) as fh:
            metadata = json.load(fh)
    else:
        git = Git(version=setup_arguments['version'])
        metadata = {
            'version': git.version
        }
        with open(METADATA_FILENAME, 'w') as fh:
            json.dump(metadata, fh)
    return metadata


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    logger.debug('Building for platform: %s', distutils.util.get_platform())

    metadata = get_and_update_metadata()
    setup_arguments['version'] = metadata['version']

    setup(**setup_arguments)
