# -*- coding: utf-8 -*-
"""
    viol.exceptions
    ~~~~~~~~~~~~~~~

    Exceptions used throughout package.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""


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
