# -*- coding: utf-8 -*-
"""
    invx.commands.completion
    ~~~~~~~~~~~~~~~~~~~~~~~~

    invx autocompletion support.  Output the bash gist to add to .bashrc for autocompletion
    of invx subcommands and flags.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""
import sys

from invx.utils.cli import Command

BASE_COMPLETION = """
# invx %(shell)s completion start%(script)s# invx %(shell)s completion end
"""

COMPLETION_SCRIPTS = {
    'bash': """
_invx_completion()
{
    COMPREPLY=( $( COMP_WORDS="${COMP_WORDS[*]}" \\
                   COMP_CWORD=$COMP_CWORD \\
                   INVX_AUTO_COMPLETE=1 $1 ) )
}
complete -o default -F _invx_completion invx
""", 'zsh': """
function _invx_completion {
  local words cword
  read -Ac words
  read -cn cword
  reply=( $( COMP_WORDS="$words[*]" \\
             COMP_CWORD=$(( cword-1 )) \\
             INVX_AUTO_COMPLETE=1 $words[1] ) )
}
compctl -K _invx_completion invx
"""}


class CompletionCommand(Command):
    """A helper command to be used for command completion."""
    name    = 'completion'
    summary = 'A helper command to be used for command completion'
    hidden  = True

    logger_level = 0    # Reduce verbosity to WARN

    def __init__(self, *args, **kw):
        super(CompletionCommand, self).__init__(*args, **kw)
        self.parser.add_option(
            '--bash', '-b',
            action='store_const',
            const='bash',
            dest='shell',
            help='Emit completion code for bash')
        self.parser.add_option(
            '--zsh', '-z',
            action='store_const',
            const='zsh',
            dest='shell',
            help='Emit completion code for zsh')

    def run(self, options, args):
        """Prints the completion code of the given shell"""
        shells = COMPLETION_SCRIPTS.keys()
        shell_options = ['--' + shell for shell in sorted(shells)]
        if options.shell in shells:
            script = COMPLETION_SCRIPTS.get(options.shell, '')
            print(BASE_COMPLETION % {'script': script, 'shell': options.shell})
        else:
            sys.stderr.write('ERROR: You must pass %s\n' % ' or '.join(shell_options))
