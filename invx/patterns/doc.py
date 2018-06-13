# -*- coding: utf-8 -*-
"""
    invx.commands.doc
    ~~~~~~~~~~~~~~~~~

    invx doc subcommand.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

from invx.utils.cli import Command
from invx.utils.log import logger
from invx.errno     import (SUCCESS, ERROR)


class DocCommand(Command):
    """Generate documentation in the specified format from standard invx input files."""
    name = 'doc'
    usage = """
      %prog [options] <package> ..."""
    summary = 'Generate documentation files from invx input files.'

    def __init__(self, *args, **kw):
        super(DocCommand, self).__init__(*args, **kw)
        self.cmd_opts.add_option(
            '-a', '--allfmts',
            dest='allfmts',
            action='store_true',
            default=False,
            help='Generate all documenation formats.')

        self.parser.insert_option_group(0, self.cmd_opts)

    def run(self, options, args):
        if not args:
            logger.warn('ERROR: Please provide a invx task or project.')
            return ERROR
        print ("subcommand: doc ", options, args)
        return SUCCESS
