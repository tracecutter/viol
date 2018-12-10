.. _prereq_lxml:

Lxml installation
=================

.. contents::

.. _install_lxml:

Overview
--------
The installation of lxml python support is not fully supported by pip on all platforms,
so it is necessary to pre-install it before installing viol.  Instructions for the
installation of lxml by platform are summarized below.  The `official installation
instructions <http://lxml.de/installation.html>`_ contain more background information.

.. _install_lxml_win:

Windows
-------
It is easiest to download and install lxml for windows for Python version 2.7
from PyPi.

Download the `latest version of lxml <https://pypi.python.org/packages/2.7/l/lxml/lxml-3.4.0.win32-py2.7.exe#md5=5a9d8e4f3f8d8d2c703a8e2f94181890>`_ for Python 2.7 from the official Website.

If you want to be sure you are installing a fully up-to-date version then use the "Windows Installer"
link from the home page of the `Python.org web site <https://pypi.python.org/pypi/lxml>`__ .

The Windows version is provided as an MSI package. To install it manually, just
double-click the file. The MSI package format allows Windows administrators to
automate installation with their standard tools.

.. _install_lxml_linux:

Linux
-----
On linux the standard pip installation functions correctly.  The installation will be
performed automatically when viol is installed, so no further steps are required.

.. _install_lxml_macosx:

Mac OS X
--------
The latest version of Mac OS X, Mavericks (v10.9), may require an update of xcode
folowed by a standard pip installation as follows

.. code-block:: console

    $ xcode-select --install
    $ pip install lxml

Older versions of Mac OS X may find it necessary to use brew to install libxml2
support.  First to `install Homebrew <https://github.com/Homebrew/homebrew/wiki/installation>`_,
simply run

.. code-block:: console

    $ ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"

The script will explain what changes it will make and prompt you before the
installation begins.  Once you've installed Homebrew, insert the Homebrew directory at the top
of your :envvar:`PATH` environment variable. You can do this by adding the following
line at the bottom of your :file:`~/.profile` file

.. code-block:: console

    export PATH=/usr/local/bin:/usr/local/sbin:$PATH

Then install libxml2 and lxml as follows

.. code-block:: console

    $ brew install libxml2
    $ pip install lxml

