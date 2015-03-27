Contributing to redislite
=========================


The redislite project always needs more people to help others. As soon as you learn redislite, you can contribute in many ways:

* Join the `pythonredislite group <https://groups.yahoo.com/neo/groups/pythonredislite/info>`_ or the pythonreddislite_ mailing list and answer questions.
* Join the `#redislite IRC channel <http://webchat.freenode.net/?channels=%23redislite&uio=d4>`_ on Freenode and answer questions. By explaining redislite to other users, you’re going to learn a lot about the module yourself.
* Report an issue_ or find a bug to fix on our issue_ tracker on github.
* Improve the documentation.
* Write unit tests.

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

Reviewing Pull Requests
-----------------------
When a pull request is submitted, three automated checks will automatically run, these checks are:

1. Check that the submitter of the pull request has a `Yahoo CLA Agreement <https://yahoocla.herokuapp.com>`_ agreement on file.
2. Check that all tests run without errors on all python releases that redislite supports.
3. Check to ensure the coverage or amount of code that is not tested did not increase.

As these checks run the pull request will be annotated with the results.  If any of these checks fail the issue found needs to be fixed before the pull request can be applied.

.. figure:: images/pull_request.png
   :scale: 50 %
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

