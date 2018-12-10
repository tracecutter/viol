# -*- coding: utf-8 -*-
"""
    viol.utils.util_str
    ~~~~~~~~~~~~~~~~~~~

    String manipulation utility calls.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""
import string
import re

from HTMLParser import HTMLParser

__all__ = ['str_to_ascii', 'str_to_int', 'str_to_bool', 'pretty_int']

# regular expresssion to process expressions and integers into normalized form
_dec_ul_re  = re.compile(r'([0123456789]+)[ULul]')
_hex_ul_re  = re.compile(r'(0[xX][0123456789abcdefABCDEF]+)[ULul]')


def str_to_ascii(text):
    """Convert a string with unicode operators to C ascii equivalents.
    """
    # convert to unicode if necessary
    if isinstance(text, str):
        text = text.decode('utf-8')

    text = text.replace(u'\u2013', '-')      # subtraction
    text = text.replace(u'\u00D7', '*')      # multiplication 1
    text = text.replace(u'\u2715', '*')      # multiplication 2
    text = text.replace(u'\uFE62', '+')      # addition
    text = text.replace(u'\u00F7', '/')      # division

    return (text.encode('utf-8'))


def str_to_int(val):
    """Convert a string to an integer (either base 10, or base 16) or return None.
    """

    if val == '1':
        return 1
    elif val == '8':
        return 8
    elif val == '7':
        return 7
    elif val == '0':
        return 0

    try:
        return int(val)             # try base 10
    except TypeError:
        return val
    except ValueError:
        # get rid of '[uUlL]' indication of unsigned/long type
        val = _dec_ul_re.sub(r'\1 ', val)
        pass

    try:
        return int(val)             # try base 10 without the [UuLl]
    except ValueError:
        # get rid of '[uUlL]' indication of unsigned/long type
        val = _hex_ul_re.sub(r'\1 ', val)
        pass

    try:
        return int(val, 16)         # try base 16 without the [UuLl]
    except:
        raise ValueError ("not an integer %r" % (val))


def str_to_bool (val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = string.lower(val)
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError ("invalid truth value %r" % (val))


def pretty_int (val):
    """Return a string with hex for numbers greater that 255, decimal otherwise."""
    if '0x' in str(val):
        return str(val)

    n = int(str(val), 0)

    if n < 255:
        return str(val)
    if (n >= 2 ** 8) and (n < 2 ** 16):
        return format (n, '#06x')

    return format (n, '#010x')
