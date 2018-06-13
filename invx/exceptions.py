# -*- coding: utf-8 -*-
"""
    invx.exceptions
    ~~~~~~~~~~~~~~~

    Exceptions used throughout package.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""


class InvxError(Exception):
    """Base invx exception"""


class BadCommand(InvxError):
    """Raised when a command is not found"""


class CommandError(InvxError):
    """Raised when there is an error in command-line arguments"""


class ParseError(InvxError):
    """Raised when an input file can't be parsed."""


class SubprocessError(InvxError):
    """Raised when there is an exit error from a subprocess (shell) command."""


class InvalidExpression(InvxError):
    """Raised when a expression evaluation went wrong"""

