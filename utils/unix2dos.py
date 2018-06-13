#! /usr/bin/env python

# Based on public domain reindent.py, by Tim Peters, 03 October 2000.

"""unix2dos [-d][-r][-v] [ path ... ]

-d (--dryrun)   Dry run.   Analyze, but don't make any changes to, files.
-r (--recurse)  Recurse.   Search for all .py files in subdirectories too.
-n (--nobackup) No backup. Does not make a ".bak" file before unix2dosing.
-v (--verbose)  Verbose.   Print informative msgs; else no output.
-h (--help)     Help.      Print this usage information and exit.

Convert files to use dos <CR><LF> line endings.

If no paths are given on the command line, unix2dos operates as a filter,
reading a single source file from standard input and writing the transformed
source to standard output.  In this case, the -d, -r and -v flags are
ignored.

You can pass one or more file and/or directory paths.  When a directory
path, all .py files within the directory will be examined, and, if the -r
option is given, likewise recursively for subdirectories.

If output is not to standard output, unix2dos overwrites files in place,
renaming the originals with a .bak extension.  If it finds nothing to
change, the file is left alone.  If unix2dos does change a file, the changed
file is a fixed-point for future runs (i.e., running unix2dos on the
resulting .py file won't change it again).

The backup file is a copy of the one that is being processed. The ".bak"
file is generated with shutil.copy(), but some corner cases regarding
user/group and permissions could leave the backup file more readable that
you'd prefer. You can always use the --nobackup option to prevent this.
"""
from __future__ import print_function

__version__ = "1"

import tokenize
import os, shutil
import sys
import re

if sys.version_info >= (3, 0):
    def tokens(readline, tokeneater):
        for token in tokenize.tokenize(readline):
            yield tokeneater(*token)
else:
    tokens = tokenize.tokenize

verbose    = 0
recurse    = 0
dryrun     = 0
makebackup = True

ext_text = ['.bat', '.cfg', '.css', '.csv', '.dot', '.dox', '.h',
            '.html', '.py', '.rst', '.t', '.txt', '.xml', '.xsd',
            '.xsl', '.gitignore', '.in', '.md', '.ini', '.rc']
ext_binary = ['.exe', '.pyc', '.ico', '.png', '.DS_Store', '.swp']

def usage(msg=None):
    if msg is not None:
        print(msg, file=sys.stderr)
    print(__doc__, file=sys.stderr)

def errprint(*args):
    sep = ""
    for arg in args:
        sys.stderr.write(sep + str(arg))
        sep = " "
    sys.stderr.write("\n")

def main():
    import getopt
    global verbose, recurse, dryrun, makebackup
    try:
        opts, args = getopt.getopt(sys.argv[1:], "drnvh",
                        ["dryrun", "recurse", "nobackup", "verbose", "help"])
    except getopt.error as msg:
        usage(msg)
        return
    for o, a in opts:
        if o in ('-d', '--dryrun'):
            dryrun += 1
        elif o in ('-r', '--recurse'):
            recurse += 1
        elif o in ('-n', '--nobackup'):
            makebackup = False
        elif o in ('-v', '--verbose'):
            verbose += 1
        elif o in ('-h', '--help'):
            usage()
            return
    if not args:
        r = Unix2Dos(sys.stdin)
        r.run()
        r.write(sys.stdout)
        return
    for arg in args:
        process(arg)

def file_is_binary(filename):
    """
    :param f: A file to examine.
    :returns: True if appears to be a binary, otherwise False.
    This routine checks if `filename` is really a file, and then uses a list
    of known extensions to determine if the file is a binary file.  If
    the extension is absent, or unknown, the first 1kb is examined and
    if the ratio of non-text is greater than 30%, then the file is
    assumed to be binary.
    """
    if not os.path.isfile(filename):
        return False
    try:
        f = open(filename)
    except IOError as msg:
        errprint("%s: I/O Error: %s" % (file, str(msg)))
        return False

    base, extension = os.path.splitext(filename)

    if extension.lower() in ext_text:
        return False

    if extension.lower() in ext_binary:
        return True

    # we don't know the extension so we use a heuristic to determine file type

    bytes_to_check = f.read(1024)
    f.close()

    textchars = ''.join(map(chr, [7,8,9,10,12,13,27] + range(0x20, 0x100)))

    # Remove the non-text chars from the bytes
    nontext = bytes_to_check.translate(None, textchars)

    # Binary if non-text chars are > 30% of the string
    nontext_ratio = float(len(nontext)) / float(len(bytes_to_check))
    return nontext_ratio > 0.3

def process(filename):
    if os.path.isdir(filename) and not os.path.islink(filename):
        if verbose:
            print("listing directory", filename)
        names = os.listdir(filename)
        for name in names:
            fullname = os.path.join(filename, name)
            if ((recurse and os.path.isdir(fullname) and
                 not os.path.islink(fullname) and
                 not os.path.split(fullname)[1].startswith("."))
                or os.path.isfile(fullname)):
                process(fullname)
        return

    if file_is_binary(filename):
        if verbose:
            print("%s is binary! Skipped." % filename)
        return

    if verbose:
        print("processing", filename, "...", end=' ')
    try:
        f = open(filename)
    except IOError as msg:
        errprint("%s: I/O Error: %s" % (filename, str(msg)))
        return

    r = Unix2Dos(f)
    f.close()
    if r.run():
        if verbose:
            print("changed.")
            if dryrun:
                print("But this is a dry run, so leaving it alone.")
        if not dryrun:
            bak = filename + ".bak"
            if makebackup:
                shutil.copyfile(filename, bak)
                if verbose:
                    print("backed up", filename, "to", bak)
            f = open(filename, "w")
            r.write(f)
            f.close()
            if verbose:
                print("wrote new", filename)
        return True
    else:
        if verbose:
            print("unchanged.")
        return False


class Unix2Dos:

    def __init__(self, f):
        # Raw file lines.
        self.raw = f.readlines()

    def run(self):
        # file after transformation.
        self.after = []
        for line in self.raw:
            line = re.sub("\r?\n", "\r\n", line)
            self.after.append(line)
        return self.raw != self.after

    def write(self, f):
        f.writelines(self.after)

if __name__ == '__main__':
    main()
