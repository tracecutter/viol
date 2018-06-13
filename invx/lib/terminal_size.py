# -*- coding: utf-8 -*-
"""
    invx.utils.terminal_size
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Cross platform terminal size utility

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""
import os
import shlex
import struct
import platform
import subprocess

"""
Except for link shortening and minor docstring edits,
this module is a verbatim copy of terminalsize.py from
https://gist.github.com/jtriley/1108174 on Feb. 19, 2013.

See also http://goo.gl/CcPZh and http://goo.gl/f9AZK
"""

__all__ = ['get_terminal_size']


def get_terminal_size():
    """
    return width and height of console; works on linux,
    os x,windows,cygwin(windows)

    based on https://gist.github.com/jtriley/1108174
    (originally retrieved from: http://goo.gl/CcPZh)

    Returns: 2-:class:`tuple` of :class:`int`
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        tuple_xy = (80, 25)      # default value
    return (tuple_xy[0], tuple_xy[1])


def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left
            sizey = bottom - top
            return (sizex, sizey)
    except:
        pass
    return None


def _get_terminal_size_tput():
    # get terminal width
    # src: http://goo.gl/f9AZK
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass
    return None


def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return (int(cr[1]), int(cr[0]))

if __name__ == "__main__":
    sizex, sizey = get_terminal_size()
    print ('width = {x} height = {h}'.format(x=sizex, h=sizey))
