.. _prereq_venv:

Virtualenv Installation
=======================

.. contents::

.. _install_venv:

Installation
------------

After Setuptools & Pip, the next development tool that you should install is
`virtualenv <http://pypi.python.org/pypi/virtualenv/>`__. Use pip

.. code-block:: console

    > pip install virtualenv

The virtualenv kit provides the ability to create virtual Python environments
that do not interfere with either each other, or the main Python installation.
If you install virtualenv before you begin coding then you can get into the
habit of using it to create completely clean Python environments for each
project. This is particularly important for Web development, where each
framework and application will have many dependencies.

The following sections describe the low-level interface to virtualenv.  Most
elect to :ref:`install virtualenvwrapper <install_venv_wrap>` to simplify the
management of multiple virtualenv sandboxes.

Create a Virtual Environment
----------------------------

To set up a new Python environment, change the working directory to wherever
you want to store the environment, and run the virtualenv utility in your
project's directory

.. code-block:: console

    > virtualenv venv

Use venv from Windows Cmd
-------------------------

To use an environment, run the :file:`activate.bat` batch file in the :file:`Scripts`
subdirectory of that environment. Your command prompt will change to show the
active environment. Once you have finished working in the current virtual
environment, run the :file:`deactivate.bat` batch file to restore your settings to
normal.

Each new environment automatically includes a copy of ``pip`` in the
:file:`Scripts` subdirectory, so that you can setup the third-party libraries and
tools that you want to use in that environment. Put your own code within a
subdirectory of the environment, however you wish. When you no longer need a
particular environment, simply copy your code out of it, and then delete the
main directory for the environment.

Use venv from Bash
------------------

To use an environment, run ``source venv/bin/activate``. Your command prompt
will change to show the active environment. Once you have finished working in
the current virtual environment, run ``deactivate`` to restore your settings
to normal.

Each new environment automatically includes a copy of ``pip``, so that you can
setup the third-party libraries and tools that you want to use in that
environment. Put your own code within a subdirectory of the environment,
however you wish. When you no longer need a particular environment, simply
copy your code out of it, and then delete the main directory for the environment.

