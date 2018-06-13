# -*- coding: utf-8 -*-
"""
    invx
    ~~~~

    invx - edf to xslx conversion utility

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

# pylint: disable=E1103

import os
import optparse
import sys

from pkg_resources          import get_distribution, DistributionNotFound
from invx.exceptions        import CommandError, InvxError
from invx.utils.util        import get_prog
from invx.utils.cli_parser  import ConfigOptionParser, UpdatingDefaultsHelpFormatter
from invx.services          import services, get_svc_summaries, get_similar_services
# XXX JCF from invx.commands          import commands, get_summaries, get_similar_commands

# This fixes a peculiarity when importing via __import__ - as we are
# initialising the invx module, "from invx import cmdoptions" is recursive
# and appears not to work properly in that situation.
import invx.utils.cli_options
cmdoptions = invx.utils.cli_options

# The version is set at build time and is in sync with setup.py and the docs conf.py
__author__      = 'John Fogelin'
__email__       = 'john@bitharmony.com'

try:
    _dist = get_distribution('invx')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, 'invx')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = 'version unknown: install invx with setup.py'
else:
    __version__ = _dist.version


def autocomplete():
    """Service, command, and option completion for the main option parser (and options).

    Enable by sourcing one of the completion shell scripts (bash or zsh).
    """
    # Don't complete if user hasn't sourced bash_completion file.
    if 'INVX_AUTO_COMPLETE' not in os.environ:
        return
    cwords = os.environ['COMP_WORDS'].split()[1:]
    cword = int(os.environ['COMP_CWORD'])
    try:
        current = cwords[cword - 1]
    except IndexError:
        current = ''

    parser = create_main_parser()

    # first we look for services in play
    services = [svc for svc, summary in get_svc_summaries()]
    try:
        service_name = [w for w in cwords if w in services][0]
    except IndexError:
        # no recognized service so let's suggest a few!
        # first check if we entering a universal command like help or completion
        subcommands = [cmd for cmd, summary in AllService.get_summaries()]
        try:
            subcommand_name = [w for w in cwords if w in subcommands][0]
        except IndexError:
            # We are here with no service or command... maybe a global option?
            # show main parser options only when necessary
            if current.startswith('-') or current.startswith('--'):
                opts = [i.option_list for i in parser.option_groups]
                opts.append(parser.option_list)
                opts = (o for it in opts for o in it)

                subcommands += [i.get_opt_string() for i in opts
                                if i.help != optparse.SUPPRESS_HELP]

            print(' '.join([x for x in subcommands if x.startswith(current)]))
            sys.exit(1)

        # We are here since we have a universal command recognized
        # special case: 'help' subcommand has no options
        if subcommand_name == 'help':
            sys.exit(1)

        # Let's suggest some useful options
        subcommand = AllService.commands[subcommand_name]()

        options += [(opt.get_opt_string(), opt.nargs)
                    for opt in subcommand.parser.option_list_all
                    if opt.help != optparse.SUPPRESS_HELP]

        # filter out previously specified options from available options
        prev_opts = [x.split('=')[0] for x in cwords[1:cword - 1]]
        options = [(x, v) for (x, v) in options if x not in prev_opts]
        # filter options by current input
        options = [(k, v) for k, v in options if k.startswith(current)]
        for option in options:
            opt_label = option[0]
            # append '=' to options which require args
            if option[1]:
                opt_label += '='
            print(opt_label)
        sys.exit(1)

    # We are here since we have a bonafide service identified

    service = services[service_name]()
    subcommands = [cmd for cmd, summary in service.get_summaries()]
    options = []
    try:
        subcommand_name = [w for w in cwords if w in subcommands][0]
    except IndexError:
        subcommand_name = None

    # subcommand options
    if subcommand_name:
        # special case: 'help' subcommand has no options
        if subcommand_name == 'help':
            sys.exit(1)

        subcommand = service.commands[subcommand_name]()
        options += [(opt.get_opt_string(), opt.nargs)
                    for opt in subcommand.parser.option_list_all
                    if opt.help != optparse.SUPPRESS_HELP]

        # filter out previously specified options from available options
        prev_opts = [x.split('=')[0] for x in cwords[1:cword - 1]]
        options = [(x, v) for (x, v) in options if x not in prev_opts]
        # filter options by current input
        options = [(k, v) for k, v in options if k.startswith(current)]
        for option in options:
            opt_label = option[0]
            # append '=' to options which require args
            if option[1]:
                opt_label += '='
            print(opt_label)
    else:
        # show main parser options only when necessary
        if current.startswith('-') or current.startswith('--'):
            opts = [i.option_list for i in parser.option_groups]
            opts.append(parser.option_list)
            opts = (o for it in opts for o in it)

            subcommands += [i.get_opt_string() for i in opts
                            if i.help != optparse.SUPPRESS_HELP]

        print(' '.join([x for x in subcommands if x.startswith(current)]))
    sys.exit(1)


def create_main_parser():
    """Beef up argparse to elegantly handle subcommands, and
    auto-completion.
    """
    parser_kw = {
        'usage': '\n%prog <command> [options]',
        'add_help_option': False,
        'formatter': UpdatingDefaultsHelpFormatter(),
        'name': 'global',
        'prog': get_prog(),
    }

    parser = ConfigOptionParser(**parser_kw)
    parser.disable_interspersed_args()

    invx_pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser.version = 'invx %s from %s (python %s)' % (
        __version__,  invx_pkg_dir, sys.version[:3])

    # add the general options
    gen_opts = cmdoptions.make_option_group(cmdoptions.general_group, parser)
    parser.add_option_group(gen_opts)

    parser.main = True  # so the help formatter knows

    # create command listing for description
    command_summaries = get_summaries()
    description = [''] + ['%-27s %s' % (i, j) for i, j in command_summaries]
    parser.description = '\n'.join(description)

    return parser


def parseopts(args):
    parser = create_main_parser()

    # Note: parser calls disable_interspersed_args(), so the result of this call
    # is to split the initial args into the general options before the
    # subcommand and everything else.
    # For example:
    #  args: ['--gen_opt=5', 'foo', '--goo', 'moo']
    #  general_options: ['--gen_opt==5']
    #  args_else: ['foo', '--goo', 'moo']
    general_options, args_else = parser.parse_args(args)

    # handle --version here
    if general_options.version:
        sys.stdout.write(parser.version)
        sys.stdout.write(os.linesep)
        sys.exit()

    # invx || invx help -> print_help()
    if not args_else or (args_else[0] == 'help' and len(args_else) == 1):
        parser.print_help()
        sys.exit()

    # the subcommand name
    cmd_name = args_else[0].lower()

    # all the args without the subcommand
    cmd_args = args[:]
    cmd_args.remove(args_else[0].lower())

    if cmd_name not in commands:
        guess = get_similar_commands(cmd_name)

        msg = ['unknown command "%s"' % cmd_name]
        if guess:
            msg.append('maybe you meant "%s"' % guess)

        raise CommandError(' - '.join(msg))

    return cmd_name, cmd_args


def main(initial_args=None):
    if initial_args is None:
        initial_args = sys.argv[1:]

    autocomplete()

    try:
        svc_name, cmd_name, cmd_args = parseopts(initial_args)
    except InvxError:
        e = sys.exc_info()[1]
        sys.stderr.write("ERROR: %s" % e)
        sys.stderr.write(os.linesep)
        sys.exit(1)

    service = services[svc_name]()
    command = service.commands[cmd_name]()
    return command.main(cmd_args)

if __name__ == '__main__':
    exit_code = main()
    if exit_code:
        sys.exit(exit_code)
