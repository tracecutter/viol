.. _contributing:

============
Contributing
============

Contributions are welcome, and they are greatly appreciated!

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Create an issue for project **Viol Design** at CreateIssue_ for the component *viol*.

.. _CreateIssue: http://xxx.xx

When creating an issue please fill out as much of each form as possible:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the JIRA issues for the project. Anything tagged with "bug"
is open to whoever wants to fix it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the JIRA feature requests for the project. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

:ref:`viol` could always use more documentation.  :ref:`viol` utilizes Sphinx_ to produce the online documentation.

.. _Sphinx: http://sphinx-doc.org/

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at CreateIssue_.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.

Get Started!
------------

Ready to contribute? Here's how to set up `viol` for local development.

1. Fork the `viol` repo
2. Clone your fork locally::

    $ git clone xxx

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv viol
    $ cd viol/
    $ python setup.py develop
    $ pip install -r requirements_dev.txt

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox::

    $ make clean-all
    $ make lint
    $ make check
    $ make test
    $ make docs-release
    $ make dist
    $ tox

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 2.7, and 3.3.

.. tip::

  To run a subset of tests::

      $ python -m unittest tests.test_viol
