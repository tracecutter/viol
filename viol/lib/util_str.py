# -*- coding: utf-8 -*-
"""
    viol.lib.util_str
    ~~~~~~~~~~~~~~~~~

    String manipulation utility calls.

    :copyright: Copyright (c) 2021 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""
import string
import re
from difflib import get_close_matches

__all__ = ['str_instance', 'str_get_similar', 'str_to_ascii', 'str_to_int', 'str_to_bool', 'pretty_int']

# regular expresssion to process expressions and integers into normalized form
_dec_ul_re  = re.compile(r'([0123456789]+)[ULul]')
_hex_ul_re  = re.compile(r'(0[xX][0123456789abcdefABCDEF]+)[ULul]')


def str_instance(instance, pretty=False):
    if instance is None:
        return '<None>'

    # Generator to filter which properties to show.
    def filter_props(obj):
        props = sorted(obj.__dict__.keys())
        for prop in props:
            if not callable(prop):
                yield (prop, getattr(obj, prop))

    prop_tuples = filter_props(instance)
    result = "<" + instance.__class__.__name__ + "("
    if pretty:
        result += "\n"
    for prop in prop_tuples:
        if pretty:
            result += "    "
        result += prop[0].__str__() + "="
        # Stylize (if desired) the output based on the type.
        # This example shortens floating point values to three decimal places.
        if isinstance(prop[1], float):
            result += "{:.3f}, ".format(prop[1])
        else:
            result += prop[1].__repr__() + ", "
        if pretty:
            result += "\n"

    result = result[:-2]
    result += ")>"
    return result


def str_get_similar(str_dict, name):
    """String to auto-correct."""
    close_strs = get_close_matches(name, list(str_dict.keys()))

    if close_strs:
        guess = close_strs[0]
    else:
        guess = False

    return guess


def str_to_ascii(text):
    """Convert a string with unicode operators to C ascii equivalents.
    """
    # convert to unicode if necessary
    if isinstance(text, str):
        text = text.decode('utf-8')

    text = text.replace('\\u2013', '-')      # subtraction
    text = text.replace('\\u00D7', '*')      # multiplication 1
    text = text.replace('\\u2715', '*')      # multiplication 2
    text = text.replace('\\uFE62', '+')      # addition
    text = text.replace('\\u00F7', '/')      # division

    return (text.encode('utf-8'))


def str_to_int(val):
    """Convert a string to an integer (either base 10, or base 16) or return None.
    """

    if val == '1':
        return 1
    if val == '8':
        return 8
    if val == '7':
        return 7
    if val == '0':
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
    except (TypeError, ValueError):
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
    if val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    raise ValueError ("invalid truth value %r" % (val))


def pretty_int (val):
    """Return a string with hex for numbers greater that 255, decimal otherwise."""
    if '0x' in str(val):
        return str(val)

    n = int(str(val), 0)

    if n < 255:
        return str(val)
    if (2 ** 8) >= n < (2 ** 16):
        return format (n, '#06x')

    return format (n, '#010x')
