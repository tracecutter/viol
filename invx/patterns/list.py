# -*- coding: utf-8 -*-
"""
    invx.commands.list
    ~~~~~~~~~~~~~~~~~~

    invx list subcommand.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

import os

from invx.listers       import listers, get_similar_lister, listers_all
from invx.utils.cli     import Command
from invx.utils         import cli_options
from invx.utils.log     import logger
from invx.exceptions    import InvxError
from invx.errno         import (SUCCESS, ERROR)


class ListCommand(Command):
    """
    List projects, tasks, and programs.

    The default logging level is quieter (WARN).  Use -v to increase verbosity.
    """
    name = 'list'

    usage = """
      %prog [options]                          # list information for default projects
      %prog [options] -a(ll) backend           # list information from all sources on backend projects
      """

    summary = 'List program information.'

    logger_level = 0    # Reduce verbosity to WARN

    def __init__(self, *args, **kw):
        super(ListCommand, self).__init__(*args, **kw)

        cmdoptions  = cli_options
        cmd_opts    = self.cmd_opts

        cmd_opts.add_option(
            '-p', '--prj',
            action='store_true',
            default=False,
            help="List project information.")

        cmd_opts.add_option(
            '-a', '--all_source',
            action='store_true',
            default=False,
            help="List object version info from all sources.")

        cmd_opts.add_option(
            '-l', '--full',
            action='store_true',
            default=False,
            help="Provide a long summary.")

        cmd_opts.add_option(
            '-b', '--brief',
            action='store_true',
            default=False,
            help="Provide only a terse summary.")

        file_locale_opts = cmdoptions.make_option_group(cmdoptions.file_locale_group, self.parser)

        self.parser.insert_option_group(0, file_locale_opts)
        self.parser.insert_option_group(0, cmd_opts)

    def run(self, options, args):
        # sanity check the arguments
        if len(args) > 1:
            logger.error ('ERROR: Too many arguments.')
            return ERROR
        elif len(args) == 1:
            arg = args[0]
        else:
            arg = None

        # if no arguments, assume we are in the invx tracking directory

        if options.root_dir is not None:
            root_dir = options.root_dir
        else:
            root_dir = os.getcwd()

        lister_list = []

        if options.prj:
            lister_list.append('prj')
        if options.all_source:
            lister_list.append('all')

        # parse the options to determine which list output format(s) are requested

        if not lister_list:
            lister_list = ['prj']
            logger.notify ('No output format specified, defaulting to "prj".')

        for lister_name in lister_list:
            if lister_name not in listers:
                guess = get_similar_lister(lister_name)
                opts = {'name': self.name, 'lister': lister_name}
                msg = ['ERROR: unknown lister "%(lister)s"' % opts]
                if guess:
                    msg.append(' - maybe you meant "%s"' % guess)
                msg.append(' (see "invx help %(name)s")' % opts)
                logger.error(''.join(msg))
                logger.error('Available outputs : %s.' % (", ".join(listers_all)))
                return ERROR

            try:
                # instantiate a lister and list information
                listers[lister_name](root_dir, arg, options)
            except InvxError as e:
                opts = {'name': self.name, 'exc': e}
                msg = ('ERROR: %(exc)s '
                       '(see "invx help %(name)s")' % opts)
                logger.error(msg)
                return ERROR

        return SUCCESS
