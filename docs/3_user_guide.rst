.. _user_guide:

User Guide
==========

.. .. contents::

Introduction
------------

.. graphviz:: viol.dot

viol provides a command line interface to the Viol Design.

viol may be used interactively, but often it often operates behind the scenes as part of
a automated test script.  It can also be useful as part of a continuous integration build
and test procedure.

.. Tip:: To obtain help for each subcommand, use the following command ``viol help <subcommand>``

.. _viol_general_options:

Usage Examples
--------------

.. code-block:: console

 viol <command> [options]

viol example 1

viol example 2

viol example 3

viol example 4

.. _config_viol:

Configuring viol
----------------

.. _config-file:

Config file
^^^^^^^^^^^

viol allows you to set all command line option defaults in a standard ini style config file.

The names and locations of the configuration files vary slightly across platforms.

* On Unix and Mac OS X the configuration file is: :file:`$HOME/.viol/viol.conf`
* On Windows, the configuration file is: :file:`%HOME%\\viol\\viol.ini`

You can set a custom path location for the config file using the environment variable ``VIOL_CONFIG_FILE``.

The names of the settings are derived from the long command line option, e.g.
if you want to use a different package index (``--index-url``) and set the
HTTP timeout (``--default-timeout``) to 60 seconds your config file would
look like this:

.. code-block:: ini

    [global]
    timeout = 60
    index-url = http://download.zope.org/ppix

Each subcommand can be configured optionally in its own section so that every
global setting with the same name will be overridden; e.g. decreasing the
``timeout`` to ``10`` seconds when running the `freeze`
(`Freezing Requirements <./#freezing-requirements>`_) command and using
``60`` seconds for all other commands is possible with:

.. code-block:: ini

    [global]
    timeout = 60

    [freeze]
    timeout = 10


Boolean options like ``--ignore-installed`` or ``--no-dependencies`` can be
set like this:

.. code-block:: ini

    [install]
    ignore-installed = true
    no-dependencies = yes

Appending options like ``--find-links`` can be written on multiple lines:

.. code-block:: ini

    [global]
    find-links =
        http://download.example.com

    [install]
    find-links =
        http://mirror1.example.com
        http://mirror2.example.com


Environment Variables
^^^^^^^^^^^^^^^^^^^^^

viol's command line options can be set with environment variables using the
format ``VIOL_<UPPER_LONG_NAME>`` . Dashes (``-``) have to be replaced with
underscores (``_``).

For example, to set the default timeout::

    export VIOL_DEFAULT_TIMEOUT=60

This is the same as passing the option to viol directly::

    viol --default-timeout=60 [...]

To set options that can be set multiple times on the command line, just add
spaces in between values. For example::

    export VIOL_FIND_LINKS="http://mirror1.example.com http://mirror2.example.com"

is the same as calling::

    viol install --find-links=http://mirror1.example.com --find-links=http://mirror2.example.com


Config Precedence
^^^^^^^^^^^^^^^^^

Command line options have precedence over environment variables, which have precedence over the config file.

Within the config file, command specific sections have precedence over the global section.

Examples:

- ``--host=foo`` overrides ``VIOL_HOST=foo``
- ``VIOL_HOST=foo`` overrides a config file with ``[global] host = foo``
- A command specific section in the config file ``[<command>] host = bar``
  overrides the option with same name in the ``[global]`` config file section

.. _viol_logging:

Logging
-------

Console logging
^^^^^^^^^^^^^^^

viol offers `-v, --verbose <--verbose>` and `-q, --quiet <--quiet>`
to control the console log level.  Each option can be used multiple times and
used together. One ``-v`` increases the verbosity by one, whereas one ``-q`` decreases it by
one.

The series of log levels, in order, are as follows::

  VERBOSE_DEBUG, DEBUG, INFO, NOTIFY, WARN, ERROR, FATAL

``NOTIFY`` is the default level.

A few examples on how the parameters work to affect the level:

* specifying nothing results in ``NOTIFY``
* ``-v`` results in ``INFO``
* ``-vv`` results in ``DEBUG``
* ``-q`` results in ``WARN``
* ``-vq`` results in ``NOTIFY``

The most practical use case for users is either ``-v`` or ``-vv`` to see
additional logging to help troubleshoot an issue.

.. _`FileLogging`:

File logging
^^^^^^^^^^^^

viol offers the `--log <--log>` option for specifying a file where a maximum
verbosity log will be kept.  This option is empty by default. This log appends
to previous logging.

Like all viol options, ``--log``, can also be set as an environment
variable, or placed into the viol config file.  See the :ref:`Configure VIOL <config_viol>`
section.


Command Completion
------------------

viol comes with support for command line completion in bash and zsh.

To setup for bash::

    $ viol completion --bash >> ~/.profile

To setup for zsh::

    $ viol completion --zsh >> ~/.zprofile

Alternatively, you can use the result of the ``completion`` command
directly with the eval function of you shell, e.g. by adding the following to your startup file::

    eval "`viol completion --bash`"
