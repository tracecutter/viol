# -*- coding: utf-8 -*-
"""
    invx.commands.help
    ~~~~~~~~~~~~~~~~~~

    invx help subcommand.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

from invx.utils.cli     import Command
from invx.exceptions    import CommandError
from invx.errno         import (SUCCESS)


class HelpCommand(Command):
    """Show help for commands"""
    name = 'help'
    usage = """
      %prog <command>"""
    summary = 'Show help for commands.'

    def run(self, options, args):
        from invx.commands import commands, get_similar_commands

        try:
            # 'invx help' with no args is handled by invx.__init__.parseopt()
            cmd_name = args[0]  # the command we need help for
        except IndexError:
            return SUCCESS

        if cmd_name not in commands:
            guess = get_similar_commands(cmd_name)

            msg = ['unknown command "%s"' % cmd_name]
            if guess:
                msg.append('maybe you meant "%s"' % guess)

            raise CommandError(' - '.join(msg))

        command = commands[cmd_name]()
        command.parser.print_help()

        return SUCCESS
