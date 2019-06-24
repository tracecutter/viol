# -*- coding: utf-8 -*-
'''
    docs.ref_gen
    ~~~~~~~~~~~~

    reference manual generator

    :copyright: Copyright (c) 2019 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
'''
import importlib
import os
import pkgutil
import click.testing
from click import core
import viol.cmds


def command_help(invocation):
    click.echo(invocation)
    click.echo('------------------------------------------------------------------------')
    click.echo('.. code-block:: none\n')
    runner = click.testing.CliRunner()
    command = invocation[5:] + ' --help'
    result = runner.invoke(viol.cmds.viol_main, command, obj={})
    output = result.output.replace('viol-main','viol')
    if result.exit_code == 0:
        click.echo('\t\t' + '\t\t'.join(output.splitlines(True)))
    else:
        click.echo(invocation + ' failed!')
        return None

def expand_help (cmds, invocation='viol'):
    # expand the subcmds of the current group
    for cmd in cmds:
        if not isinstance(cmd, click.Group):
            command_help (invocation + ' ' + cmd.name)

    # expand the subgroup commands
    for cmd in cmds:
        if isinstance(cmd, click.Group):
            new_inv = invocation + ' ' + cmd.name
            command_help (new_inv)
            cmd_mod = importlib.import_module('viol.cmds.' + cmd.name)
            cmd_subcmds = '_'.join(new_inv.split(' ') + ['cmds'])
            expand_help(getattr(cmd_mod, cmd_subcmds), new_inv)

click.echo('.. AUTO-GENERATED FILE - DO NOT EDIT!! Use `make ref`.')
click.echo('.. _reference:')
click.echo('')
click.echo('Reference Guide')
click.echo('===============')
click.echo('')


# Start with top level viol help
command_help('viol')

# Recursively expand all subcommand help
expand_help(viol.cmds.viol_cmds)
