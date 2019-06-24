# -*- coding: utf-8 -*-
"""
    viol.cmds.completion
    ~~~~~~~~~~~~~~~~~~~~

    Output script to append to .bashrc or .zshrc in order to enable autocompletion from the shell.

    :copyright: Copyright (c) 2019 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

from __future__ import absolute_import

import logging
import click

logger = logging.getLogger(__name__)


@click.command()
@click.option('--shell-type', type=click.Choice(['bash', 'zsh']), default='bash',
              help='A helper command to be used for command completion.')
def completion(shell_type):
    """A helper command to be used for command completion.

    Append the output of this command to your shell .rc file.  When executed,
    striking tab during command line interaction will autocomplete and/or suggest
    possible input.  Command options are enumerated if tab is struck after the
    character '-' is input.
    """
    logger.debug('Outputting shell rc script for {}.'.format(shell_type))
    if shell_type == 'bash':
        logger.info('eval "$(_VIOL_COMPLETE=source viol)"')
    else:
        logger.info('eval "$(_VIOL_COMPLETE=source_zsh viol)"')
