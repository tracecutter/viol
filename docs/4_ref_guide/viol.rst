viol
----

.. contents::

Usage
*****

::

 viol <command> [options]


Description
***********

.. graphviz:: viol.dot

viol provides a command line interface to the Viol Design.

viol may be used interactively, but often it often operates behind the scenes as part of
a automated test script.  It can also be useful as part of a continuous integration build
and test procedure.


.. Tip:: To obtain help for each subcommand, use the following command ``viol help <subcommand>``


.. _viol_logging:

Logging
=======

Console logging
~~~~~~~~~~~~~~~

viol offers :ref:`-v, --verbose <--verbose>` and :ref:`-q, --quiet <--quiet>`
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
~~~~~~~~~~~~

viol offers the :ref:`--log <--log>` option for specifying a file where a maximum
verbosity log will be kept.  This option is empty by default. This log appends
to previous logging.

Additionally, when commands fail (i.e. return a non-zero exit code), viol writes
a "failure log" for the failed command. This log overwrites previous
logging. The default location is as follows:

* On Unix and Mac OS X: :file:`$HOME/.viol/viol.log`
* On Windows, the configuration file is: :file:`%HOME%\\viol\\viol.log`

The option for the failure log, is :ref:`--log-file <--log-file>`.

Both logs add a line per execution to specify the date and what viol executable wrote the log.

Like all viol options, ``--log`` and ``log-file``, can also be set as an environment
variable, or placed into the viol config file.  See the :ref:`Configure VIOL <config_viol>`
section.


.. _viol_general_options:

General Options
***************

.. viol-general-options::

