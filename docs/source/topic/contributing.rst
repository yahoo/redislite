Contributing to redislite
=========================

First steps
-----------

The redislite project always needs more people to help others. As soon as you learn redislite, you can contribute in many ways:

* Join the `pythonredislite group <https://groups.yahoo.com/neo/groups/pythonredislite/info>`_ or the pythonreddislite_ mailing list and answer questions.
* Join the `#redislite IRC channel <http://webchat.freenode.net/?channels=%23redislite&uio=d4>`_ on Freenode and answer questions. By explaining redislite to other users, you’re going to learn a lot about the module yourself.
* Report an issue_ or find a bug to fix on our issue_ tracker on github.
* Improve the documentation.
* Write unit tests.  


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



Building Codebase Familiarity by Reviewing Pull Requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Look at pull requests to build familiarity with the codebase and the process.  Provide comments and feedback if you see issues or can provide more information.

Some things to look for:

* See if the code is missing docs or tests.
* Look through the changes a pull request makes, and keep an eye out for syntax that is incompatible with older but still supported versions of Python.
* Make sure all the tests run and pass under all versions of python.
* Leave comments and feedback!
* Often times the codebase will change between a patch being submitted and the time it gets reviewed. Make sure it an older pull request still aapplies cleanly to the Master branch and functions as expected.


Writing code
------------

Coding style
~~~~~~~~~~~~
Code submitted to :mod:`redislite` should be compliant with the python pep8_ style guide.

Prior to submitting code, check for pep8_ conformance by running::

    tox -e pep8

Then fix any issues.



Check Code for Common Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Before submitting a pull request it's a good idea to run a code analysis tool to identify any common errors and indicators of bad code.  Using python tools such as pylint_ or flake8.

This can be done by running::

    tox -e pylint


Testing
~~~~~~~~~~
Any changes to source code should be tested, both for regression and for validation of new code.
All tests can be run using the tox tool without any arguments::

    tox

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



.. _pep8: http://www.python.org/dev/peps/pep-0008/
.. _pylint: http://pypi.python.org/pypi/pylint
.. _rst: http://docutils.sourceforge.net/docs/user/rst/quickstart.html
.. _fork: https://guides.github.com/activities/forking/



Improvements to documentation
--------------------------

Writing documentation
~~~~~~~~~~~~~~~~~~~~~~~~
The redislite documentation is good but it can always be improved. Did you find a typo? Do you think that something
should be clarified? Go ahead and update the documentation in the docs/source directory.

Once your documentation changes have been made, run the following to generate the html documentation.::

    tox -e build_docs

Then open the ``build/sphinx/html/index.html`` file in your web browser to ensure the generated documentation looks
correct.

Once the documentation looks correct, go ahead and submit a pull request.


Writing style
~~~~~~~~~~~~~
Code submitted to :mod:`redislite` should be compliant with the python pep8_ style guide.

Prior to submitting code, check for pep8_ conformance by running::

    tox -e pep8

Then fix any issues.



FAQ
---

How can I help with triaging?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If there is an uncommented issue that reports a bug, try and reproduce it. If you can reproduce it and it seems valid, add a comment that you confirmed the bug. Consider writing a code to test for the bug’s behavior, even if you don’t fix the bug itself.








Submitting Code
---------------
To submit your code for inclusion upstream, do the following to ensure your
submission only includes your new changes:

1.  Make sure you have Completed a `Yahoo CLA Agreement <https://yahoocla.herokuapp.com>`_.
2.  Redislite development occurs on github at: https://github.com/yahoo/redislite.  All 
    development should occur on a fork of the redislite github repo.
3.  Prior to submitting a pull request, perform a merge from the MASTER branch of the main
    redislite repository into your fork.  This will ensure your pull request only includes your
    changes and will allow you to deal with any upstream changes that affect
    your code.
4.  Clear up all PEP8 issues before submission.  This will ensure your changesets only 
    include code changes and not formatting changes.
5.  Clear up or document exceptions for all PyLint/Flake8 issues.  This will
    ensure the evaluation and review of your code does not have common coding
    errors and decrease the human time to evaluate changes.

Reviewing Pull Requests
-----------------------
When a pull request is submitted, three automated checks will automatically run, these checks are:

1. Check that the submitter of the pull request has a `Yahoo CLA Agreement <https://yahoocla.herokuapp.com>`_ agreement on file.
2. Check that all tests run without errors on all python releases that redislite supports.
3. Check to ensure the coverage or amount of code that is not tested did not increase.

As these checks run the pull request will be annotated with the results.  If any of these checks fail the issue found needs to be fixed before the pull request can be applied.

.. figure:: pull_request.png
   :scale: 25%
   :alt: A successful pull request

   An example of a pull request that successfully passed all automated checks.

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

.. _pythonredislitegroup: https://groups.yahoo.com/neo/groups/pythonredislite/info

.. _pythonreddislite: pythonredislite-subscribe@yahoogroups.com

.. _redislite: http://webchat.freenode.net/?channels=%23redislite&uio=d4

.. _issue: https://github.com/yahoo/redislite/issues


.. _Note: the following sections are set not to show.
.. _I am not sure how this is programmed.
.. _but I want to make sure that they remain so that the work of naming them is not lost.
.. _These lines comment out when '.. _' is used in front of the text.
.. _But below this is not used but still the sections do not show.
.. _I assume that it is programmed to be like that when converted from reSt to Sphynx.
.. _So these sections are saved and when new text is put in the section can show simply
.. _by re-indenting the text to the left margin.
.. _These sections may be added back piecemeal in the future.

    Reporting bugs
    ~~~~~~~~~~~~~~

    Requesting features
    ~~~~~~~~~~~~~~~~~~~

    How we make decisions
    ~~~~~~~~~~~~~~~~~~~~~

    Triaging tickets
    ----------------

    Triage workflow
    ~~~~~~~~~~~~~~~

    Triage stages
    ~~~~~~~~~~~~~

    Other triage attributes
    ~~~~~~~~~~~~~~~~~~~~~~~

    Closing Tickets
    ~~~~~~~~~~~~~~~

    Submitting patches
    ~~~~~~~~~~~~~~~~~~

    Working with Git and GitHub
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Writing documentation
    ---------------------

    Getting the raw documentation
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Getting started with Sphinx
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Writing style
    ~~~~~~~~~~~~~

    Commonly used terms
    ~~~~~~~~~~~~~~~~~~~

    Guidelines for reStructuredText files
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Documenting new features
    ~~~~~~~~~~~~~~~~~~~~~~~~

    An example
    ~~~~~~~~~~

    Improving the documentation
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Spelling check
    ~~~~~~~~~~~~~~

    Committing code
    ---------------

    Commit access
    ~~~~~~~~~~~~~

    Handling pull requests
    ~~~~~~~~~~~~~~~~~~~~~~

    Committing guidelines
    ~~~~~~~~~~~~~~~~~~~~~

    Reverting commits
    ~~~~~~~~~~~~~~~~~
