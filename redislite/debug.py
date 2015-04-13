from __future__ import print_function
from distutils.spawn import find_executable
from .__init__ import __version__, __git_version__, __source_url__, \
    __git_hash__, __git_origin__, __git_branch__, __redis_server_info__, \
    __redis_executable__
import os


def print_debug_info():
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
