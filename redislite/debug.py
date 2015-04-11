from __future__ import print_function
from .__init__ import __version__, __git_version__, __source_url__, \
    __git_hash__, __git_origin__, __git_branch__


if __name__ == '__main__':  # pragma: no cover
    print("Redislite debug information:")
    print('\tVersion: %s' % __version__)
    print('')
    print('\tSource Code Information')
    if __git_version__:
        print('\t\tGit Source URL: %s' % __source_url__)
        print('\t\tGit Hash: %s' % __git_hash__)
        print('\t\tGit Version: %s' % __git_version__)
        print('\t\tGit Origin: %s' % __git_origin__)
        print('\t\tGit Branch: %s' % __git_branch__)
