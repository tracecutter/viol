# -*- coding: utf-8 -*-
"""
    invx.commands
    ~~~~~~~~~~~~~

    Package containing all invx subcommands

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

from invx.commands.list         import ListCommand
from invx.commands.show         import ShowCommand
from invx.commands.search       import SearchCommand
from invx.commands.doc          import DocCommand
from invx.commands.completion   import CompletionCommand
from invx.commands.help         import HelpCommand


commands = {
    CompletionCommand.name: CompletionCommand,
    DocCommand.name: DocCommand,
    HelpCommand.name: HelpCommand,
    ListCommand.name: ListCommand,
    SearchCommand.name: SearchCommand,
    ShowCommand.name: ShowCommand,
}


commands_order = [
    ListCommand,
    ShowCommand,
    SearchCommand,
    DocCommand,
    HelpCommand,
]


def get_summaries(ignore_hidden=True, ordered=True):
    """Yields sorted (command name, command summary) tuples."""

    if ordered:
        cmditems = _sort_commands(commands, commands_order)
    else:
        cmditems = commands.items()

    for name, command_class in cmditems:
        if ignore_hidden and command_class.hidden:
            continue

        yield (name, command_class.summary)


def get_similar_commands(name):
    """Command name auto-correct."""
    from difflib import get_close_matches

    close_commands = get_close_matches(name, commands.keys())

    if close_commands:
        guess = close_commands[0]
    else:
        guess = False

    return guess


def _sort_commands(cmddict, order):
    def keyfn(key):
        try:
            return order.index(key[1])
        except ValueError:
            # unordered items should come last
            return 0xff

    return sorted(cmddict.items(), key=keyfn)
