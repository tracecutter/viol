# -*- coding: utf-8 -*-
"""
    viol.cmds.help
    ~~~~~~~~~~~~~~

    A help command as alternative to --help option.

    :copyright: Copyright (c) 2021 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""


import logging
import click
from viol.lib.util_str import str_get_similar

logger = logging.getLogger(__name__)


@click.command()
@click.argument('subcmd', default=None, required=False, nargs=1)
@click.pass_context
def help(ctx, subcmd, **kw):
    """Show help for commands.

    This command provides an alternative to --help option to provide usage information.
    """
    if subcmd is not None:
        if subcmd in ctx.parent.command.commands:
            help_msg = ctx.parent.command.commands[subcmd].get_help(ctx)
            click.echo(help_msg.replace('viol help', 'viol ' + subcmd))
        else:
            guess = str_get_similar(ctx.parent.command.commands, subcmd)
            if guess:
                click.secho('ERROR: unknown viol subcommand "{}" - maybe you meant "{}"'.format(subcmd, guess),
                            fg='red')
            else:
                click.secho('ERROR: unknown viol subcommand "{}".'.format(subcmd), fg='red')
    else:
        click.echo(ctx.parent.get_help())
