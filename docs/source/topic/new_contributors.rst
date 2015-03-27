Advice for new contributors
===========================

New contributor and not sure what to do? Want to help but just don’t know how to get started? This is the section for you.

First steps
-----------
Start with these easy tasks to contribute to redislite.

Sign the Contributor License Agreement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Prior to submitting a pull request, please complete a `Yahoo CLA Agreement <https://yahoocla.herokuapp.com>`_.

Set up Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
All redislite development uses the python `tox` tool.

Install it with the python pip packaging tool, like this::

    pip install tox

Writing documentation for redislite just requires a working python with the tox python package installed.

Running and testing code requires a working python development environment and c compiler sufficient to compile redis.

Redislite Development Site
~~~~~~~~~~~~~~~~~~~~~~~~~~
Redislite development occurs on github at:
https://github.com/yahoo/redislite

All development should occur on a fork_ or branch of the redislite github repo.

Triage issues
~~~~~~~~~~~~~
If there is an uncommented issue that reports a bug, try and reproduce it. If you can reproduce it and it seems valid, add a comment that you confirmed the bug. Consider writing a code to test for the bug’s behavior, even if you don’t fix the bug itself.

Reviewing Pull Requests
~~~~~~~~~~~~~~~~~~~~~~~
Look at pull requests to build familiarity with the codebase and the process.  Provide comments and feedback if you see issues or can provide more information.

Some things to look for:
* See if the code is missing docs or tests.
* Look through the changes a pull request makes, and keep an eye out for syntax that is incompatible with older but still supported versions of Python.
* Make sure all the tests run and pass under all versions of python.
* Leave comments and feedback!
* Often times the codebase will change between a patch being submitted and the time it gets reviewed. Make sure it an older pull request still aapplies cleanly to the Master branch and functions as expected.

Write some documentation
~~~~~~~~~~~~~~~~~~~~~~~~
The redislite documentation is good but it can always be improved. Did you find a typo? Do you think that something should be clarified? Go ahead and update the documentation in the docs/source directory and submit a pull request.
See also the guide on Writing documentation, in particular the tips for Improving the documentation.

Once your documentation changes have been made, run the following to generate the html documentation.::

    tox -e build_docs

Then open the ``build/sphinx/html/index.html`` file in your web browser to ensure the generated documentation looks correct.


Testing
-------
Any changes to source code should be tested, both for regression and for validation of new code.

Running all tests
~~~~~~~~~~~~~~~~~
All tests can be run using the tox tool without any arguments::

    tox


Style Check
~~~~~~~~~~~
Code submitted to `redislite` should be compliant with the python [pep8] style guide.

Prior to submitting code, check for [pep8] conformance by running::

    tox -e pep8

Then fix any issues.

Check Code for Common Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Before submitting a pull request it's a good idea to run a code analysis tool to identify any common errors and indicators of bad code.  Using python tools such as [pylint] or [flake8].

This can be done by running::

    tox -e pylint


Unit Tests
~~~~~~~~~~
Working unit tests are required for all code that adds new functionality.  Running the unit tests will generate a coverage report at the end of the test output.  The report should show 100% coverage on all code.  The report looks like::

    Name                      Stmts   Miss Branch BrMiss  Cover   Missing
    ---------------------------------------------------------------------
    redislite                     6      0      0      0   100%
    redislite.client            122      0     22      0   100%
    redislite.configuration      11      0      0      0   100%
    redislite.patch              41      0     12      0   100%
    ---------------------------------------------------------------------
    TOTAL                       180      0     34      0   100%
    ----------------------------------------------------------------------

To see this report, run::

    tox

CI Pipelines
------------
Any new change branches should build correctly using CI prior to being submitted
for upstream inclusion.

Local changes can be tested by running::

    tox

in the git root directory.

When a pull request is submitted the travis-ci service will automatically run
the tests on the code in the pull request and annotate the pull request with the
results.

Pull requests should never be submitted before the travis-ci pipeline indicates
the tests all pass.


Submitting Code
---------------
To submit your code for inclusion upstream, do the following to ensure your
submission only includes your new changes:

1.  Make sure you have Completed a `Yahoo CLA Agreement <https://yahoocla.herokuapp.com>`_.
2.  Perform a merge from the MASTER branch of the main redislite repository
    into your fork.  This will ensure your pull request only includes your
    changes and will allow you to deal with any upstream changes that affect
    your code.
3.  Clear up all PEP8 issues before submission.  This will ensure your
    changesets only include code changes and not formatting changes.
4.  Clear up or document exceptions for all PyLint/Flake8 issues.  This will
    ensure the evaluation and review of your code does not have common coding
    errors and decrease the human time to evaluate changes.

[pep8]: http://www.python.org/dev/peps/pep-0008/
[pylint]: http://pypi.python.org/pypi/pylint
[markdown]: http://daringfireball.net/projects/markdown/
[rst]: http://docutils.sourceforge.net/docs/user/rst/quickstart.html
[fork]: https://guides.github.com/activities/forking/

