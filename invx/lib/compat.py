# -*- coding: utf-8 -*-
"""
    invx.utils.compat
    ~~~~~~~~~~~~~~~~~

    invx platform/os compatibility support.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

# flake8: noqa
# pylint: disable=E0601

import os
import imp
import sys
import site


"""
These utility functions resolve differences between Python versions and platform distributions.
"""

__all__ = ['WindowsError']

uses_pycache = hasattr(imp, 'cache_from_source')


class NeverUsedException(Exception):
    """this exception should never be raised"""

try:
    WindowsError = WindowsError
except NameError:
    WindowsError = NeverUsedException

try:
    #new in Python 3.3
    PermissionError = PermissionError
except NameError:
    PermissionError = NeverUsedException

console_encoding = sys.__stdout__.encoding


try:
    unicode

    def binary(s):
        if isinstance(s, unicode):
            return s.encode('ascii')
        return s
except NameError:
    def binary(s):
        if isinstance(s, str):
            return s.encode('ascii')


if sys.version_info >= (3,):
    from io import StringIO

    def cmp(a, b):
        return (a > b) - (a < b)

    def b(s):
        return s.encode('utf-8')

    def u(s):
        try:
            return s.decode('utf-8')
        except UnicodeDecodeError:
            return s.decode('ISO-8859-1')

    def console_to_str(s):
        try:
            return s.decode(console_encoding)
        except UnicodeDecodeError:
            try:
                return s.decode('utf-8')
            except UnicodeDecodeError:
                return s.decode('ISO-8859-1')

    def get_http_message_param(http_message, param, default_value):
        return http_message.get_param(param, default_value)

else:
    from cStringIO import StringIO

    def b(s):
        return s

    def u(s):
        return s

    def console_to_str(s):
        return s

    def get_http_message_param(http_message, param, default_value):
        result = http_message.getparam(param)
        return result or default_value

    cmp = cmp


# packages in the stdlib that may have installation metadata, but should not be
# considered 'installed'.  this theoretically could be determined based on
# dist.location (py27:`sysconfig.get_paths()['stdlib']`,
# py26:sysconfig.get_config_vars('LIBDEST')), but fear platform variation may
# make this ineffective, so hard-coding
stdlib_pkgs = ['python', 'wsgiref']
if sys.version_info >= (2, 7):
    stdlib_pkgs.extend(['argparse'])
