# -*- coding: utf-8 -*-
"""
    invx.commands.search
    ~~~~~~~~~~~~~~~~~~~~

    invx search subcommand.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

from invx.utils.cli         import Command
from invx.utils.cli_args    import cli_args_to_invx_objects
from invx.utils             import cli_options
from invx.utils.log         import logger
from invx.errno             import (SUCCESS, ERROR)


class SearchCommand(Command):
    """
    Search for resources (projects, tasks, ...)  that match a command line query.

    The default logging level for this routine is lowered to WARN.  Use -v to increase verbosity.
    """
    name = 'search'

    usage = """
      %prog [options] <query>        # project names, resources, glob patterns
      %prog [options] --gen-cli ...  # convert wildcard query to explicit object selection
      """

    summary = 'Search for objects and modules whose name contains <query>.'

    logger_level = 0    # Reduce verbosity to WARN

    def __init__(self, *args, **kw):
        super(SearchCommand, self).__init__(*args, **kw)

        cmdoptions  = cli_options
        cmd_opts    = self.cmd_opts

        cmd_opts.add_option(
            '-x', '--exclude',
            dest='invx_object_exclude_list',
            default=[],
            action='append',
            metavar='tobj',
            help="Exclude invx resources that match this glob pattern, dir, or file listing objects.")

        cmd_opts.add_option(
            '-b', '--brief',
            action='store_true',
            default=False,
            help="Provide only a terse summary.")

        cmd_opts.add_option(
            '-g', '--gen-cli',
            action='store_true',
            default=False,
            help="Generate an unabiguous, search free, command line option string to specify valid objects.")

        file_locale_opts = cmdoptions.make_option_group(cmdoptions.file_locale_group, self.parser)

        self.parser.insert_option_group(0, file_locale_opts)
        self.parser.insert_option_group(0, cmd_opts)

    def run(self, options, args):
        logger.banner (logger.NOTIFY, '%s: Start' % self.name.capitalize())

        # parse the command line arguments (and options) into a invx_objects and chip_config

        (status, options, invx_objects) = cli_args_to_invx_objects(self.name, options, args)

        if (status == ERROR):   # error reporting already completed
            return ERROR

        logger.banner (logger.NOTIFY, '%s: Search Library Objects' % self.name.capitalize())

        for invx_object in invx_objects:
            if options.gen_cli:
                print (invx_object.gen_cli())
            else:
                print (invx_object.info(options.brief))

        logger.banner (logger.NOTIFY, '%s: Complete' % self.name.capitalize())

        return SUCCESS
