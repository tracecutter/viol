# -*- coding: utf-8 -*-
"""
    viol.cmds
    ~~~~~~~~~

    viol subcommands

    :copyright: Copyright (c) 2021 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""


import logging
import logging.config
from configparser import ConfigParser
import click
from viol import __version__
from viol.exceptions import CustomExceptionHandler, click_exception_handler
from viol.lib.log import setup_logging, indent_log
from viol.lib.util_str import str_instance
from viol.cmds.scan import scan
from viol.cmds.help import help
from viol.cmds.completion import completion

logger = logging.getLogger(__name__)

# pylint: disable=E1103

DEFAULT_CFG = 'viol.conf'


class ViolCtx(object):

    def __init__(self):
        self.config = {}
        self.verbosity = 0

    def __repr__(self):
        return(str_instance(self))


pass_viol_ctx = click.make_pass_decorator(ViolCtx)


def configure(ctx, param, filename):
    cfg = ConfigParser()
    cfg.read(filename)
    ctx.default_map = {}
    for sect in cfg.sections():
        command_path = sect.split('.')
        if command_path[0] != 'jenc':
            continue
        defaults = ctx.default_map
        for cmdname in command_path[1:]:
            defaults = defaults.setdefault(cmdname, {})
        defaults.update(cfg[sect])


@click.group(invoke_without_command=True,
             context_settings=dict(max_content_width=132, auto_envvar_prefix='VIOL'),
             cls=CustomExceptionHandler(click.Group, handler=click_exception_handler,
                                        ignore_args=['--log']))
@click.option('--config', '--c', type=click.Path(dir_okay=False),
              default=DEFAULT_CFG, callback=configure, is_eager=True, expose_value=False, show_default=True,
              help='Read option defaults from the specified INI file')
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
    # note that all subcmd __init__ files (and therefore Click subcmds are built from bottom up
    # Create a viol_ctx object and store it in the click context object.
    ctx.obj = ViolCtx()
    ctx.obj.verbosity = verbose - quiet

    # Setup logging to console and append to a user_log_file if selected
    setup_logging(verbosity=ctx.obj.verbosity, no_color=not color, user_log_file=logfile)
    pass

    # To debug option processing
    logger.debug('jenc_main ctx:')
    with indent_log(4):
        logger.debug (str_instance(ctx, pretty=True))

    pass


viol_cmds = [scan, completion, help]
# now we add all subcmds (and subgroups)
for cmd in viol_cmds:
    logger.debug('Adding {}'.format(cmd))
    viol_main.add_command(cmd)
