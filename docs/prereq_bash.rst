.. _prereq_bash:

Bash Integration
================

.. contents::

.. _install_bash:

Overview
--------
Interactive use of invx via the bash shell is optional.  Quite often invx simply
operates in the background in a supporting role to build scripts, and other
continuous integration activities.  On Windows, invx can be used directly from
the command prompt or powershell.  So if a richer command line interface is of
no interest, you can skip the instructions here.

On Mac OS X and Linux, bash is already fully integrated into the operating system
so skip to the `Bash Configuration`_ section below.

For those interested in a Windows bash shell with most of the common Unix
command line utilities suchas *grep*, *sed*, *find*, etc... read on!

.. _prereq_bash_win:

Windows Installation
--------------------

There are two common approaches to providing a bash shell to Windows.

Cygwin
^^^^^^
For a full featured, "faithful" implementation of Unix, many turn to
`Cygwin <https://www.cygwin.com/>`_.  This is a comparibly large
installation, that touches the windows registry, and is generally more
intrusive.  While recent support has improved, Cygwin has often demonstrated
unreliability in conjunction with new Windows releases, and can interact
poorly with other native windows utilities.  Most Cygwin users are better
served by a proper Linux virtual machine.  `Virtual Box <https://www.virtualbox.org/>`_
provides a perfectly adequate, free, virtual machine to run a linux
distribution of your choosing.  Ubuntu is generally the most consumer
oriented, and a good default choice.  The downside of both Cygwin and a
virtual machine appraoch is the anachronistic integration with the Windows native
utilities, and files.  If the goal is to turn your PC into a Unix box, just
partition your drive and do so!

If, on the other hand, you are interested in a bash shell that includes a sensible
collection of frequently used unix commands on a PC that's *primary* role is
windows development, there is a better, lighter weight, alternative.

Basic MSYS/Git/Bash for Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
There is a build environment -- also known as msysgit -- for `Git for
Windows <http://msysgit.github.io/>`__.  It turns out to be the
easiest way to get a lightweight unix shell on Windows.  A fringe
benefit of this installation is the inclusion of `git <http://git-scm.com/>`_,
a popular decentralized revision control utility.

If you only want the bare minimum Unix-type command-line shell, install it via the
`Download <https://github.com/msysgit/msysgit/releases/download/Git-1.9.4-preview20140929/Git-1.9.4-preview20140929.exe>`__.

This environment is sufficient for basic development, but you may
want to enhance your environment by downloading `make <http://repo.or.cz/w/msysgit.git?a=blob;f=bin/make.exe;h=a971ea1266ff40e89137bba068e2c944a382725f;hb=968336eddac1874c56cd934d10783566af5a3e26>`__,
rename it ``make.exe``, and add it to your ``$PATH``.

If you elect to install virtualenvwrapper (See :ref:`install_venv_wrap`), you will also need
to install `mktemp <http://sourceforge.net/projects/mingw/files/MSYS/Extension/mktemp/mktemp-1.6-2/mktemp-1.6-2-msys-1.0.13-bin.tar.lzma/download>`__, and add it to your ``$PATH``.

Included Components:

-  Bash, a Unix-type command-line shell.
-  Git, a popular distributed revision control system

Full MSYS/Git/Bash for Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For an even more full featured Unix environment, that includes the GNU
C Compiler, GNU Make, and other useful Unix features (including mktemp),
install msysgit via the `net installer
<https://github.com/msysgit/msysgit/releases>`__. This
installer will clone `two <http://github.com/msysgit/msysgit>`__
`repositories <http://github.com/msysgit/git>`__, including all the
necessary components to build Git for Windows, and perform an initial
build.

Included Components:

-  Bash, a Unix-type command-line shell.
-  Git, a popular distributed revision control system
-  The GNU C Compiler.
-  GNU Make.
-  Perl.
-  Tcl/Tk, a scripting language making it easy to implement
   cross-platform graphical user interfaces.
-  `cURL <http://curl.haxx.se>`__, a library implementing HTTP and FTP transport.
-  additional libraries.
-  even more Unix programs

The relationship between *msysGit*, *Git for Windows*, and *Cygwin*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Git for Windows <https://github.com/msysgit/msysgit/releases>`__ is the
software package that installs a minimal environment to run Git on
Windows. It comes with a Bash (a Unix-type shell), with a Perl
interpreter and with the Git executable and its dependencies.

On the other hand, msysGit is the software package installing the *build
environment* that can build Git for Windows. The easiest way is to
install it via the `net
installer <https://github.com/msysgit/msysgit/releases>`__.

The difference between MSys and MinGW
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The `MinGW project <http://mingw.org/>`__'s goal is to provide a way to
compile native Windows binaries with no POSIX layer using the GNU C
Compiler.

However, Bash requires at least a POSIX layer (most notably due to the
absence of the ``fork()`` call on Windows). Therefore, MSys (the
*minimal system*) is thrown in, offering the minimal system necessary to
offer Bash (and Perl) functionality on Windows.

Consequently, MSys ships with a POSIX layer (based on an old version of
Cygwin) that is only used by the Bash and Perl, but not by anything
compiled within that environment.

Further information
^^^^^^^^^^^^^^^^^^^

For more information and documentation, please have a look and enhance
our `Wiki <https://github.com/msysgit/msysgit/wiki>`__.

For code contributions and discussions, please see our `mailing
list <http://groups.google.com/group/msysgit>`__.

Bash Configuration
------------------

Regardless of which bash shell installation strategy has been chosen, it
must be configured to provide full functionality.  The key user configuration
files for bash are *~/.bashrc* and *~/.profile*.

invx includes support for command line completion in bash and zsh.

To setup for bash::

    $ invx completion --bash >> ~/.profile

To setup for zsh::

    $ invx completion --zsh >> ~/.zprofile

Alternatively, you can use the result of the ``completion`` command
directly with the eval function of you shell, e.g. by adding the following to your startup file::

    eval "`invx completion --bash`"

