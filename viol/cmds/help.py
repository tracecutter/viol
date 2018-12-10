# -*- coding: utf-8 -*-
"""
    viol.commands.help
    ~~~~~~~~~~~~~~~~~~

    viol help subcommand.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

from viol.utils.cli     import Command
from viol.exceptions    import CommandError
from viol.errno         import (SUCCESS)


class HelpCommand(Command):
    """Show help for commands"""
    name = 'help'
    usage = """
      %prog <command>"""
    summary = 'Show help for commands.'

    def run(self, options, args):
        from viol.commands import commands, get_similar_commands

        try:
            # 'viol help' with no args is handled by viol.__init__.parseopt()
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
