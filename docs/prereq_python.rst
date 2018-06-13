.. _prereq_python:

Python Installation
===================

.. contents::

.. _prereq_python_install:

Installation
------------

Instructions for the installation of Python by platform are summarized below.

Once installed, you do not need to install or configure anything else to use Python.
Having said that, it is strongly encouraged that you install the tools and
libraries described in subsequent install guides before you start building Python
applications for real-world use. In particular, you should always install
Setuptools, Pip, Virtualenv, and Virtualenvwrapper — they make it much easier
for you to use other third-party Python libraries.

.. _prereq_python_win:

Windows
-------
First, download the `latest version of Python 2.7 <http://python.org/ftp/python/2.7.6/python-2.7.6.msi>`_
from the official Website. If you want to be sure you are installing a fully
up-to-date version then use the "Windows Installer" link from the home page of the
`Python.org web site <http://python.org>`__ .

The Windows version is provided as an MSI package. To install it manually, just
double-click the file. The MSI package format allows Windows administrators to
automate installation with their standard tools.

By design, Python installs to a directory with the version number embedded,
e.g. Python version 2.7 will install at :file:`C:\\Python27\\`, so that you can
have multiple versions of Python on the
same system without conflicts. Of course, only one interpreter can be the
default application for Python file types. It also does not automatically
modify the :envvar:`PATH` environment variable, so that you always have control over
which copy of Python is run.

Typing the full path name for a Python interpreter each time quickly gets
tedious, so add the directories for your default Python version to the :envvar:`PATH`.
Assuming that your Python installation is in :file:`C:\\Python27\\`, add this to your
:envvar:`PATH`:

.. code-block:: console

    C:\Python27\;C:\Python27\Scripts\

You can do this easily by running the following in ``powershell``:

.. code-block:: console

    [Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\Python27\;C:\Python27\Scripts\", "User")

The second (:file:`Scripts`) directory receives command files when certain
packages are installed, so it is a very useful addition.


Linux
-----

Most Linux distributions include Python.  If so, you do not need to install or configure
anything else to use Python.  For instance, the latest versions of Ubuntu and Fedora **come
with Python 2.7 out of the box**.

The latest versions of Redhat Enterprise (RHEL) and CentOS come with Python 2.6.
Some older versions of RHEL and CentOS come with Python 2.4 which is
unacceptable for modern Python development. Fortunately, there are
`Extra Packages for Enterprise Linux`_ which include high
quality additional packages based on their Fedora counterparts. This
repository contains a Python 2.6 package specifically designed to install
side-by-side with the system's Python 2.4 installation.

.. _Extra Packages for Enterprise Linux: http://fedoraproject.org/wiki/EPEL

Mac OS X
--------

The latest version of Mac OS X, Mavericks, **comes with Python 2.7 out of the box**.

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

    export PATH=/usr/local/bin:/usr/local/sbin:$PATH

Now, we can install Python 2.7:

.. code-block:: console

    $ brew install python

