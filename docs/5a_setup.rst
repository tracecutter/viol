.. _setup:

Development Setup
=================

viol works on Windows, Unix/Linux, and Mac OS X.

viol requires Python and works on versions 2.6 or later, and 3.x.  However, for better compatibility
with other python tools, CPython version 2.7 is preferred.

Python Installation
-------------------

.. contents::

.. _prereq_python_install:

Installation
^^^^^^^^^^^^

Instructions for the installation of Python by platform are summarized below.

Once installed, you do not need to install or configure anything else to use Python.
Having said that, it is strongly encouraged that you install the tools and
libraries described in subsequent install guides before you start building Python
applications for real-world use. In particular, you should always install
Setuptools, Pip, Virtualenv, and Virtualenvwrapper — they make it much easier
for you to use other third-party Python libraries.

Linux
^^^^^

Virtually all Linux distributions include Python.  Thus, you do not need to install or configure
anything else to use Python.  For instance, the latest versions of Ubuntu and Fedora **come
with Python 2.7 out of the box**.

Mac OS X
^^^^^^^^

The latest version of Mac OS X, **comes with Python 2.7 out of the box**.

For older versions of Mac OS X, the version of Python that ships with OS X is great
for learning. Yet, it's not good for development. The version shipped with OS X may
be out of date from the
`official current Python release <https://www.python.org/downloads/mac-osx/>`_,
which is considered the stable production version.

To update to a different version of Python, you'll need to install GCC. GCC can be obtained
by downloading `XCode <http://developer.apple.com/xcode/>`_, the smaller
`Command Line Tools <https://developer.apple.com/downloads/>`_ (must have an
Apple account) or the even smaller `OSX-GCC-Installer <https://github.com/kennethreitz/osx-gcc-installer#readme>`_
package.

.. note::
    If you already have XCode installed, do not install OSX-GCC-Installer.
    In combination, the software can cause issues that are difficult to
    diagnose.

If you already of XCode installed, update the latest version

.. code-block:: console

    $ xcode-select --install

While OS X comes with a large number of UNIX utilities, those familiar with
Linux systems will notice one key component missing: a decent package manager.
`Homebrew <http://brew.sh>`_ fills this void.

To `install Homebrew <https://github.com/Homebrew/homebrew/wiki/installation>`_,
simply run

.. code-block:: console

    $ ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"

The script will explain what changes it will make and prompt you before the
installation begins.
Once you've installed Homebrew, insert the Homebrew directory at the top
of your :envvar:`PATH` environment variable. You can do this by adding the following
line at the bottom of your :file:`~/.profile` file

.. code-block:: console

Pip Installation
----------------

The Python community has settled on **pip** as the standard packaging and
distribution mechanism.  Once you add pip to your Python system you can download
and install any compliant Python software product with a single command. It also
enables you to add this network installation capability to your own Python software
with very little work.  Pip builds upon **Setuptools**, and provides both
install and uninstall support.  Pip also provides for installation from locally
hosted packages and offers VCS integration.

To install pip (and setuptools), run the Python script available here:
`get-pip.py <https://raw.github.com/pypa/pip/master/contrib/get-pip.py>`_

    export PATH=/usr/local/bin:/usr/local/sbin:$PATH

Now, we can install Python 2.7:

.. code-block:: console

    $ brew install python

Bash Integration
----------------

.. contents::

.. _install_bash:

Overview
^^^^^^^^
Interactive use of viol via the bash shell is optional.  Quite often viol simply
operates in the background in a supporting role to build scripts, and other
continuous integration activities.  On Windows, viol can be used directly from
the command prompt or powershell.  So if a richer command line interface is of
no interest, you can skip the instructions here.

On Mac OS X and Linux, bash is already fully integrated into the operating system
so skip to the `Bash Configuration`_ section below.

For those interested in a Windows bash shell with most of the common Unix
command line utilities suchas *grep*, *sed*, *find*, etc... read on!

Bash Configuration
^^^^^^^^^^^^^^^^^^

Regardless of which bash shell installation strategy has been chosen, it
must be configured to provide full functionality.  The key user configuration
files for bash are *~/.bashrc* and *~/.profile*.

viol includes support for command line completion in bash and zsh.

To setup for bash::

    $ viol completion --bash >> ~/.profile

To setup for zsh::

    $ viol completion --zsh >> ~/.zprofile

Alternatively, you can use the result of the ``completion`` command
directly with the eval function of you shell, e.g. by adding the following to your startup file::

    eval "`viol completion --bash`"

Virtualenv Installation
-----------------------

.. contents::

.. _install_venv:

Installation
^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To set up a new Python environment, change the working directory to wherever
you want to store the environment, and run the virtualenv utility in your
project's directory

.. code-block:: console

    > virtualenv venv

Use venv from Bash
^^^^^^^^^^^^^^^^^^

To use an environment, run ``source venv/bin/activate``. Your command prompt
will change to show the active environment. Once you have finished working in
the current virtual environment, run ``deactivate`` to restore your settings
to normal.

Each new environment automatically includes a copy of ``pip``, so that you can
setup the third-party libraries and tools that you want to use in that
environment. Put your own code within a subdirectory of the environment,
however you wish. When you no longer need a particular environment, simply
copy your code out of it, and then delete the main directory for the environment.


Virtualenvwrapper Installation
------------------------------

.. contents::

.. _install_venv_wrap:

Installation
^^^^^^^^^^^^
The design goal of virtualenvwrapper is to ease usage of Ian Bicking's
`virtualenv <http://pypi.python.org/pypi/virtualenv>`__, a tool for creating isolated Python
virtual environments, each with their own libraries and site-packages.

The virtualenvwrapper provides a collection of convenience functions to work with
virtual environments.

Bash Install
^^^^^^^^^^^^

On Linux, and Mac OS X, after installing virtualenv, install
`virtualenvwrapper <http://pypi.python.org/pypi/virtualenvwrapper/>`__. Use pip

.. code-block:: console

    $ pip install virtualenvwrapper

Usage
^^^^^

Main Commands
"""""""""""""
``mkvirtualenv <name>``
    Create a new virtualenv environment named *<name>*.  The environment will
    be created in WORKON_HOME.

``lsvirtualenv``
    List all of the enviornments stored in WORKON_HOME.

``rmvirtualenv <name>``
    Remove the environment *<name>*. Uses ``folder_delete.bat``.

``workon [<name>]``
    If *<name>* is specified, activate the environment named *<name>* (change
    the working virtualenv to *<name>*). If a project directory has been
    defined, we will change into it. If no argument is specified, list the
    available environments.

``deactivate``
    Deactivate the working virtualenv and switch back to the default system
    Python.

``add2virtualenv <full or relative path>``
    If a virtualenv environment is active, appends *<path>* to
    ``virtualenv_path_extensions.pth`` inside the environment's site-packages,
    which effectively adds *<path>* to the environment's PYTHONPATH.
    If a virtualenv environment is not active, appends *<path>* to
    ``virtualenv_path_extensions.pth`` inside the default Python's
    site-packages. If *<path>* doesn't exist, it will be created.

Convenience Commands
""""""""""""""""""""
``cdproject``
    If a virtualenv environment is active and a projectdir has been defined,
    change the current working directory to active virtualenv's project directory.
    ``cd-`` will return you to the last directory you were in before calling
    ``cdproject``.

``cdsitepackages``
    If a virtualenv environment is active, change the current working
    directory to the active virtualenv's site-packages directory. If
    a virtualenv environment is not active, change the current working
    directory to the default Python's site-packages directory. ``cd-``
    will return you to the last directory you were in before calling
    ``cdsitepackages``.

``cdvirtualenv``
    If a virtualenv environment is active, change the current working
    directory to the active virtualenv base directory. If a virtualenv
    environment is not active, change the current working directory to
    the base directory of the default Python. ``cd-`` will return you
    to the last directory you were in before calling ``cdvirtualenv``.

``lssitepackages``
    If a virtualenv environment is active, list that environment's
    site-packages. If a virtualenv environment is not active, list the
    default Python's site-packages. Output includes a basic listing of
    the site-packages directory, the contents of easy-install.pth,
    and the contents of virtualenv_path_extensions.pth (used by
    ``add2virtualenv``).

``setprojectdir <full or relative path>``
    If a virtualenv environment is active, define *<path>* as project
    directory containing the source code.  This allows the use of ``cdproject``
    to change the working directory. In addition, the directory will be
    added to the environment using ``add2virtualenv``. If *<path>* doesn't
    exist, it will be created.

``toggleglobalsitepackages``
    If a virtualenv environment is active, toggle between having the
    global site-packages in the PYTHONPATH or just the virtualenv's
    site-packages.

``whereis <file>``
    A script included for convenience. Returns directory locations
    of `file` and `file` with any executable extensions. So you can call
    ``whereis python`` to find all executables starting with ``python`` or
    ``whereis python.exe`` for an exact match.

