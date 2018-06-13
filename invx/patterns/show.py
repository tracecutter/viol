# -*- coding: utf-8 -*-
"""
    invx.commands.show
    ~~~~~~~~~~~~~~~~~~

    invx show subcommand. Show invx resource information.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

from invx.utils.cli      import Command
from invx.utils.cli_args import cli_args_to_invx_objects
from invx.utils          import cli_options
from invx.utils.log      import logger
from invx.errno          import (SUCCESS, ERROR)


class ShowCommand(Command):
    """
    Summarize basic information on selected (excluded) invx resources.

    The default logging level for this routine is lowered to WARN.  Use -v to increase verbosity.
    """
    name = 'show'

    usage = """
      %prog [options]                               # summarize all default invx resources
      """

    summary = 'Summarize invx basic information.'

    logger_level = 0    # Reduce verbosity to WARN

    def __init__(self, *args, **kw):
        super(ShowCommand, self).__init__(*args, **kw)

        cmdoptions = cli_options
        cmd_opts = self.cmd_opts

        cmd_opts.add_option(
            '-x', '--exclude',
            dest='invx_object_exclude_list',
            default=[],
            action='append',
            metavar='tobj',
            help="Exclude Txxx objects that match this glob pattern, dir, or file listing objects.")

        cmd_opts.add_option(
            '-b', '--brief',
            action='store_true',
            default=False,
            help="Provide only a terse summary.")

        file_locale_opts = cmdoptions.make_option_group(cmdoptions.file_locale_group, self.parser)

        self.parser.insert_option_group(0, file_locale_opts)
        self.parser.insert_option_group(0, cmd_opts)

    def run(self, options, args):
        logger.banner (logger.NOTIFY, '%s: Start' % self.name.capitalize())

        # parse the command line arguments (and options) into a invx_objects and chip_config

        (status, options, invx_objects) = cli_args_to_invx_objects(self.name, options, args)

        if (status == ERROR):   # error reporting already completed
            return ERROR

        logger.banner (logger.NOTIFY, '%s: Show Summary for selected resources' % self.name.capitalize())

        for invx_object in invx_objects:
            print (invx_object.info(options.brief))

        logger.banner (logger.NOTIFY, '%s: Complete' % self.name.capitalize())

        return SUCCESS
