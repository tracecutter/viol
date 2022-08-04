# -*- coding: utf-8 -*-
"""
    viol.exceptions
    ~~~~~~~~~~~~~~~

    Exceptions used throughout package.

    :copyright: Copyright (c) 2021 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

import sys
import click
from click.exceptions import UsageError, BadParameter, BadOptionUsage, NoSuchOption
from viol.errno import ERROR
from viol.lib.util_str import str_instance, str_get_similar


class ViolError(Exception):
    """Base viol exception"""


class BadCommand(ViolError):
    """Raised when a command is not found"""


class CommandError(ViolError):
    """Raised when there is an error in command-line arguments"""


class ParseError(ViolError):
    """Raised when an input file can't be parsed."""


class SubprocessError(ViolError):
    """Raised when there is an exit error from a subprocess (shell) command."""


def CustomExceptionHandler(cls, handler, ignore_args=None):
    """A super class to allow viol to customize exception handling of underlying class."""

    class Cls(cls):

        _original_args = None
        _command = None

        def make_context(self, info_name, args, parent=None, **extra):
            # grab the original command line arguments
            self._original_args = ' '.join(args)

            # if only options and no command, show help
            no_cmd = True
            for n, arg in enumerate(args):
                if arg[0] != '-':
                    # ignore options that take an argument, and don't mistake them for a command
                    if n > 0 and args[n - 1] in ignore_args:
                        continue
                    self._command = arg
                    no_cmd = False
                    break

            if no_cmd:
                args.insert(0, '--help')

            try:
                return super().make_context(info_name, args, parent=parent, **extra)
            except Exception as exc:
                # call the handler
                handler(self, info_name, exc, None)

                # let the user see the original error
                raise

        def invoke(self, ctx):
            try:
                return super().invoke(ctx)
            except Exception as exc:
                # call the handler
                handler(self, ctx.info_name, exc, ctx)

                # let the user see the original error
                raise

        def __repr__(self):
            return(str_instance(self))

    return Cls


def click_exception_handler(cmd, info_name, exc, ctx):
    '''Catch click exceptions in order to improve Usage response.'''
    if isinstance(exc, UsageError) and ctx is not None and ctx.command.commands:
        if not isinstance(exc, (BadParameter, BadOptionUsage, NoSuchOption)):
            guess = str_get_similar(ctx.command.commands, cmd._command)
            if guess:
                click.secho('ERROR: unknown command "{}" - maybe you meant "{}"'.format(cmd._command, guess), fg='red')
            else:
                click.secho('ERROR: {}'.format(exc.message), fg='red')
            sys.exit(ERROR)
