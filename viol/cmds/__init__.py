# -*- coding: utf-8 -*-
"""
    viol.cmds
    ~~~~~~~~~

    viol subcommands

    :copyright: Copyright (c) 2019 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""
from __future__ import absolute_import
from __future__ import division

import logging
import logging.config
import click
from viol import __version__
from viol.exceptions import CustomExceptionHandler, click_exception_handler
from viol.lib.log import setup_logging
from viol.cmds.scan import scan
from viol.cmds.help import help
from viol.cmds.completion import completion

logger = logging.getLogger(__name__)

# pylint: disable=E1103


class ViolCtx(object):

    def __init__(self):
        self.config = {}
        self.verbosity = 0

    def set_config(self, key, value):
        self.config[key] = value
        logger.debug('config[%s] = %s' % (key, value))

    def __repr__(self):
        # Generator to filter which properties to show.
        # This example excludes properties prefixed with "_" and methods.
        def filter_props(obj):
            props = sorted(obj.__dict__.keys())
            for prop in props:
                if not callable(prop) and prop[0] != "_":
                    yield (prop, getattr(obj, prop))
            return

        prop_tuples = filter_props(self)
        result = "<" + self.__class__.__name__ + "("
        for prop in prop_tuples:
            result += prop[0].__str__() + "="
            # Stylize (if desired) the output based on the type.
            # This example shortens floating point values to three decimal places.
            if isinstance(prop[1], float):
                result += "{:.3f}, ".format(prop[1])
            else:
                result += prop[1].__repr__() + ", "

        result = result[:-2]
        result += ")>"
        return result


pass_viol_ctx = click.make_pass_decorator(ViolCtx)


@click.group(context_settings=dict(max_content_width=120),
             cls=CustomExceptionHandler(click.Group, handler=click_exception_handler,
                                        ignore_args=['--log']))
@click.version_option(__version__, '--version', '-V')
@click.option('--verbose', '-v', count=True,
              help='Give more output. Increase verbosity: option is additive up to 3 times.')
@click.option('--quiet', '-q', count=True,
              help='Give less output. Decrease verbosity: option is additive up to 3 times.' +
              ' (WARNING, ERROR, CRITICAL)')
@click.option('--log', 'logfile', default=None, type=click.Path(),
              help='Path to a verbose appending log.')
@click.option('--color/--no-color', default=True,
              help='Enable/Suppress colored output.')
@click.pass_context
def viol_main(ctx, verbose, quiet, logfile, color):
    '''viol is a command line tool to administer the Viol Design.'''
    # Create a viol_ctx object and store it in the click context object.
    ctx.obj = ViolCtx()
    ctx.obj.verbosity = verbose - quiet
    # Setup logging to console and append to a user_log_file if selected
    setup_logging(verbosity=ctx.obj.verbosity, no_color=not color, user_log_file=logfile)
    pass


viol_cmds = [scan, completion, help]
# now we add all subcmds (and subgroups)
for cmd in viol_cmds:
    logger.debug('Adding {}'.format(cmd))
    viol_main.add_command(cmd)
