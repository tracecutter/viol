# -*- coding: utf-8 -*-
"""
    viol.utils.util
    ~~~~~~~~~~~~~~~

    viol native OS utility call support.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""
import sys
import os
import re
import fnmatch
import subprocess
from viol.exceptions     import SubprocessError
from viol.utils.log      import logger
from viol.utils.compat   import console_to_str

__all__ = ['display_path', 'backup_dir', 'normalize_name', 'format_size',
           'make_path_relative', 'pretty_path', 'normalize_path', 'split_leading_dir',
           'has_leading_dir', 'get_prog', 'call_subprocess', 'find_file', 'find_file_list',
           'find_dir_list', 'is_dirname', 'is_glob', 'ffs_lsb', 'ffs_msb']

# ignore a few problematic directories that trick the search for viol resources
_search_excludes = ['Tests', 'tests', '.svn', '.git']


def ffs_lsb (val):
    """Return the bit position (1 base counting) of the least significant bit set."""
    return (((1 + (val ^ (val - 1))) >> 1).bit_length())


def ffs_msb (val):
    """Return the bit position (1 base counting) of the most significant bit set."""
    return (val.bit_length())


def get_prog():
    try:
        if os.path.basename(sys.argv[0]) in ('__main__.py', '-c'):
            return "%s -m viol" % sys.executable
    except (AttributeError, TypeError, IndexError):
        pass
    return 'viol'


def display_path(path):
    """Gives the display value for a given path, making it relative to cwd
    if possible."""
    path = os.path.normcase(os.path.abspath(path))
    if path.startswith(os.getcwd() + os.path.sep):
        path = '.' + path[len(os.getcwd()):]
    return path


def backup_dir(bu_dir, ext='.bak'):
    """Figure out the name of a directory to back up the given dir to
    (adding .bak, .bak2, etc)"""
    n = 1
    extension = ext
    while os.path.exists(bu_dir + extension):
        n += 1
        extension = ext + str(n)
    return bu_dir + extension


def ask(message, options):
    """Ask the message interactively, with the given possible responses"""
    while 1:
        response = raw_input(message)
        response = response.strip().lower()
        if response not in options:
            print('Your response (%r) was not one of the expected responses: %s' % (
                response, ', '.join(options)))
        else:
            return response

_normalize_re = re.compile(r'[^a-z]', re.I)


def normalize_name(name):
    return _normalize_re.sub('-', name.lower())


def is_dirname(path, basename):
    """Check if `path` points to a directory named `basename`."""
    path = normalize_path(path)
    return ((path is not None) and
            (os.path.isdir(path) and (os.path.basename(path) == basename)))


def find_file(path=None, depth=4, strict=False, pattern='[pP]*[0-9].xml', search_excludes=None):
    """
    Search a `path` for a file that matches a `pattern` up to a `depth` or sub-directories.
    Search only sub-directories of exact `depth` if `strict` is True.
    """
    return find_file_list(path, depth, strict, pattern, search_excludes, first_match=True)


def find_file_list(path=None, depth=4, strict=False, pattern='[pP]*[0-9].xml', search_excludes=None,
                   first_match=False):
    """
    Search a `path` for files that match a `pattern` up to a `depth` or sub-directories.
    Search only sub-directories of exact `depth` if `strict` is True.
    """
    match = []
    if (path is None):
        path = normalize_path(os.getcwd())
    else:
        path = normalize_path(path)

    if (not os.path.isdir(path)):
        logger.warn('WARNING: Search path is not a directory "%s".' % pretty_path(path))
        return []

    if search_excludes is None:
        search_excludes = _search_excludes

    if depth == 0:
        files = os.listdir(path)
        for f in fnmatch.filter(files, pattern):
            match.append(os.path.join(path, f))
            if first_match:
                return match
        return match

    for root, dirs, files in os.walk(path, topdown=True):
        current_depth = root[len(path):].count(os.path.sep)
        dirs[:] = [d for d in dirs if d not in search_excludes]
        if (strict and (current_depth == depth)) or (not strict and current_depth <= depth):
            files[:] = [f for f in files if f not in search_excludes]
            for f in fnmatch.filter(files, pattern):
                match.append(os.path.join(root, f))
                if first_match:
                    return match
        elif current_depth > depth:
            dirs[:] = []    # Don't recurse any deeper than depth
    return match


def find_dir_list(path=None, depth=2, strict=False, pattern='[pP][0-9]*', search_excludes=None):
    """
    Search a `path` for directories that match a `pattern` up to a `depth` or sub-directories.
    Search only sub-directories of exact `depth` if `strict` is True.
    """
    match = []
    if (path is None):
        path = normalize_path(os.getcwd())
    else:
        path = normalize_path(path)

    if (not os.path.isdir(path)):
        logger.warn('WARNING: Search path is not a directory "%s".' % pretty_path(path))
        return []

    if search_excludes is None:
        search_excludes = _search_excludes

    for root, dirs, files in os.walk(path, topdown=True):
        current_depth = root[len(path) + len(os.path.sep):].count(os.path.sep)
        dirs[:] = [d for d in dirs if d not in search_excludes]
        if (strict and (current_depth == (depth - 1))) or (not strict and current_depth <= depth):
            for d in fnmatch.filter(dirs, pattern):
                match.append(os.path.join(root, d))
        elif current_depth > depth:
            dirs[:] = []    # Don't recurse any deeper than depth
    return match


def is_glob(glob):
    """Check whether `glob` contains ANY of the chars in '\\*!?[]'"""
    return True in [c in glob for c in "*!?[]"]


def format_size(nbytes):
    if nbytes > 1000 * 1000:
        return '%.1fMB' % (nbytes / 1000.0 / 1000)
    elif nbytes > 10 * 1000:
        return '%ikB' % (nbytes / 1000)
    elif nbytes > 1000:
        return '%.1fkB' % (nbytes / 1000.0)
    else:
        return '%ibytes' % nbytes


def split_leading_dir(path):
    path = str(path)
    path = path.lstrip('/').lstrip('\\')
    if '/' in path and (('\\' in path and path.find('/') < path.find('\\')) or ('\\' not in path)):
        return path.split('/', 1)
    elif '\\' in path:
        return path.split('\\', 1)
    else:
        return path, ''


def has_leading_dir(paths):
    """Returns true if all the paths have the same leading path name
    (i.e., everything is in one subdirectory in an archive)"""
    common_prefix = None
    for path in paths:
        prefix, rest = split_leading_dir(path)
        if not prefix:
            return False
        elif common_prefix is None:
            common_prefix = prefix
        elif prefix != common_prefix:
            return False
    return True


def make_path_relative(path, rel_to):
    """
    Make a filename relative, where the filename path, and it is
    relative to rel_to

        >>> make_relative_path('/usr/share/something/a-file.pth',
        ...                    '/usr/share/another-place/src/Directory')
        '../../../something/a-file.pth'
        >>> make_relative_path('/usr/share/something/a-file.pth',
        ...                    '/home/user/src/Directory')
        '../../../usr/share/something/a-file.pth'
        >>> make_relative_path('/usr/share/a-file.pth', '/usr/share/')
        'a-file.pth'
    """
    path_filename = os.path.basename(path)
    path = os.path.dirname(path)
    path = os.path.normpath(os.path.abspath(path))
    rel_to = os.path.normpath(os.path.abspath(rel_to))
    path_parts = path.strip(os.path.sep).split(os.path.sep)
    rel_to_parts = rel_to.strip(os.path.sep).split(os.path.sep)
    while path_parts and rel_to_parts and path_parts[0] == rel_to_parts[0]:
        path_parts.pop(0)
        rel_to_parts.pop(0)
    full_parts = ['..'] * len(rel_to_parts) + path_parts + [path_filename]
    if full_parts == ['']:
        return '.' + os.path.sep
    return os.path.sep.join(full_parts)


def pretty_path(path):
    """
    Make a filename path relative to current working directory.
    """
    if (path is None):
        return 'None'

    pretty = (make_path_relative (normalize_path(path), normalize_path(os.getcwd())))
    if (pretty != path) and (pretty[0] != os.path.sep) and (pretty[0] != '.'):
        pretty = "." + os.path.sep + pretty

    if len(pretty) >= len(path):  # longer is not pretty!
        pretty = path

    return pretty


def normalize_path(path):
    """
    Convert a path to its canonical, case-normalized, absolute version.

    """
    if path is None:
        return None
    else:
        return os.path.normcase(os.path.realpath(os.path.expanduser(path)))


def call_subprocess(cmd, show_stdout=True, log_stdout=False, log_progress=False,
                    filter_stdout=None, cwd=None, raise_on_returncode=True,
                    command_level=logger.DEBUG, command_desc=None, extra_environ=None):
    if command_desc is None:
        cmd_parts = []
        for part in cmd:
            if ' ' in part or '\n' in part or '"' in part or "'" in part:
                part = '"%s"' % part.replace('"', '\\"')
            cmd_parts.append(part)
        command_desc = ' '.join(cmd_parts)
    if show_stdout:
        stdout = None
    else:
        stdout = subprocess.PIPE
    logger.log(command_level, "Running command %s" % command_desc)
    env = os.environ.copy()
    if extra_environ:
        env.update(extra_environ)
    try:
        proc = subprocess.Popen(
            cmd, stderr=subprocess.STDOUT, stdin=None, stdout=stdout,
            cwd=cwd, env=env)
    except Exception:
        e = sys.exc_info()[1]
        logger.fatal(
            "Error %s while executing command %s" % (e, command_desc))
        raise
    all_output = []

    # if stdout is available via a pipe, it's time to drain it
    if stdout is not None:
        stdout = proc.stdout
        while True:
            line = console_to_str(stdout.readline())
            if not line:
                break
            line = line.rstrip()
            if filter_stdout:
                line = filter_stdout(line)
            if (line is not None) and (line != ''):
                all_output.append(line + '\n')
            if log_stdout:
                logger.info(line)
            if log_progress:
                logger.show_progress()
    else:
        returned_stdout, returned_stderr = proc.communicate()
        all_output = []
        for i, line in enumerate(returned_stdout):
            if filter_stdout:
                line = filter_stdout(line)
                if (line is not None) and (line != ''):
                    all_output.append(line)
            else:
                all_output.append(line)

        if not all_output:
            all_output = ['']

    proc.wait()
    if proc.returncode:
        if raise_on_returncode:
            if all_output:
                logger.notify('Complete output from command %s:' % command_desc)
                logger.notify('\n'.join(all_output) +
                              '\n----------------------------------------')
            raise SubprocessError(
                "Command %s failed with error code %s in %s"
                % (command_desc, proc.returncode, cwd))
        else:
            logger.warn(
                "Command %s had error code %s in %s"
                % (command_desc, proc.returncode, cwd))

    return all_output
