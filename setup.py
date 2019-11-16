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
import os
import sys
from subprocess import call, check_output, CalledProcessError


logger = logging.getLogger(__name__)

UNSUPPORTED_PLATFORMS = ['win32', 'win64']
METADATA_FILENAME = 'redislite/package_metadata.json'
BASEPATH = os.path.dirname(os.path.abspath(__file__))
REDIS_PATH = os.path.join(BASEPATH, 'redis.submodule')
REDIS_SERVER_METADATA = {}
install_scripts = ''
try:
    VERSION = check_output(['meta', 'get', 'package.version']).decode(errors='ignore')
except:
    VERSION = '5.0.5'


class BuildRedis(build):
    global REDIS_SERVER_METADATA

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
    build_scripts = None

    def initialize_options(self):
        install.initialize_options(self)

    def finalize_options(self):
        install.finalize_options(self)
        self.set_undefined_options('build', ('build_scripts', 'build_scripts'))

    def run(self):
        global install_scripts
        # run original install code
        install.run(self)

        # install Redis executables
        logger.debug(
            'running InstallRedis %s -> %s', self.build_lib, self.install_lib
        )
        self.copy_tree(self.build_lib, self.install_lib)
        module_bin = os.path.join(self.install_lib, 'redislite/bin')
        if not os.path.exists(module_bin):
            os.makedirs(module_bin, 0o0755)
        self.copy_tree(self.build_scripts, module_bin)
        logger.debug(
            'running InstallRedis %s -> %s',
            self.build_scripts, self.install_scripts
        )
        self.copy_tree(self.build_scripts, self.install_scripts)

        install_scripts = self.install_scripts
        print('install_scripts: %s' % install_scripts)
        md_file = os.path.join(
            self.install_lib, 'redislite/package_metadata.json'
        )
        if os.path.exists(md_file):
            with open(md_file) as fh:
                md = json.load(fh)
                if os.path.exists(os.path.join(module_bin, 'redis-server')):
                    md['redis_bin'] = os.path.join(module_bin, 'redis-server')
                else:
                    md['redis_bin'] = os.path.join(
                        install_scripts, 'redis-server'
                    )
            # Store the redis-server --version output for later
            for line in os.popen('%s --version' % md['redis_bin']).readlines():
                line = line.strip()
                for item in line.split():
                    if '=' in item:
                        key, value = item.split('=')
                        REDIS_SERVER_METADATA[key] = value
            md['redis_server'] = REDIS_SERVER_METADATA
            print('new metadata: %s' % md)
            with open(md_file, 'w') as fh:
                json.dump(md, fh, indent=4)

# Create a dictionary of our arguments, this way this script can be imported
#  without running setup() to allow external scripts to see the setup settings.
args = {
    'package_data': {
        'redislite': ['package_metadata.json', 'bin/redis-server'],
    },
    'include_package_data': True,
    'cmdclass': {
        'build': BuildRedis,
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
    global METADATA_FILENAME
    global REDIS_SERVER_METADATA

    if not os.path.exists('.git') and os.path.exists(METADATA_FILENAME):
        with open(METADATA_FILENAME) as fh:
            metadata = json.load(fh)
    else:
        git = Git(version=VERSION)
        metadata = {
            'git_origin': git.origin,
            'git_branch': git.branch,
            'git_hash': git.hash,
            'redis_server': REDIS_SERVER_METADATA,
            'redis_bin': install_scripts
        }
        with open(METADATA_FILENAME, 'w') as fh:
            json.dump(metadata, fh, indent=4)
    return metadata


if __name__ == '__main__':
    if sys.platform in UNSUPPORTED_PLATFORMS:
        print(
            'The redislite module is not supported on the %r '
            'platform' % sys.platform,
            file=sys.stderr
        )
        sys.exit(1)

    os.environ['CC'] = 'gcc'

    logging.basicConfig(level=logging.INFO)

    logger.debug('Building for platform: %s', distutils.util.get_platform())

    metadata = get_and_update_metadata()

    setup(**setup_arguments)
