#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Checker for file headers
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Make sure each Python file has a correct file header
    including copyright and license information.

    :copyright: Copyright (c) 2018 Bit Harmony Ltd.. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""
from __future__ import print_function

import sys, os, re
from six import StringIO
from optparse import OptionParser
from os.path import join, splitext, abspath


checkers = {}

def checker(*suffixes, **kwds):
    only_pkg = kwds.pop('only_pkg', False)
    def deco(func):
        for suffix in suffixes:
            checkers.setdefault(suffix, []).append(func)
        func.only_pkg = only_pkg
        return func
    return deco

# Default values
verbose = False
llength = 100    # line length limit

copyright_re = re.compile(br'^    :copyright: Copyright \(c\) 20\d\d(-20\d\d)? '
                          br'Bit Harmony Ltd. All rights reserved. See AUTHORS.\n')
license_re   = re.compile(br"    :license: (.*?).\n")
coding_re    = re.compile(br'coding[:=]\s*([-\w.]+)')
not_ix_re    = re.compile(br'\bnot\s+\S+?\s+i[sn]\s\S+')
is_const_re  = re.compile(br'if.*?==\s+(None|False|True)\b')

# flag these commonly misspeled words
misspellings = [b"developement", b"adress",             # ALLOW-MISSPELLING
                b"verificate", b"informations",         # ALLOW-MISSPELLING
                b" xxx ", b"fixme", b"todo",            # ALLOW-MISSPELLING
                b"fuck", b"shit", b" ass ", b"cunt",    # ALLOW-MISSPELLING
                ]

if sys.version_info < (3, 0):
    @checker('.py')
    def check_syntax(fn, lines):
        try:
            compile(b''.join(lines), fn, "exec")
        except SyntaxError as err:
            yield 0, "not compilable: %s" % err


@checker('.py')
def check_style_and_encoding(fn, lines):
    encoding = 'ascii'
    for lno, line in enumerate(lines):
        if len(line) > llength:
            yield lno+1, "line too long"
        if lno < 2:
            co = coding_re.search(line)
            if co:
                encoding = co.group(1).decode('ascii')
        if line.strip().startswith(b'#'):
            continue
        #m = not_ix_re.search(line)
        #if m:
        #    yield lno+1, '"' + m.group() + '"'
        if is_const_re.search(line):
            yield lno+1, 'using == None/True/False'
        try:
            line.decode(encoding)
        except UnicodeDecodeError as err:
            yield lno+1, "not decodable: %s\n   Line: %r" % (err, line)
        except LookupError as err:
            yield 0, "unknown encoding: %s" % encoding
            encoding = 'latin1'


@checker('.py', only_pkg=True)
def check_fileheader(fn, lines):
    # line number correction
    c = 1
    if lines[0:1] == [b'#!/usr/bin/env python\n']:
        lines = lines[1:]
        c = 2

    llist = []
    docopen = False
    for lno, l in enumerate(lines):
        llist.append(l)
        if lno == 0:
            if l == b'# -*- coding: rot13 -*-\n':
                # special-case pony package
                return
            elif l != b'# -*- coding: utf-8 -*-\n':
                yield 1, "missing coding declaration"
        elif lno == 1:
            if l != b'"""\n' and l != b'r"""\n':
                yield 2, 'missing docstring begin (""")'
            else:
                docopen = True
        elif docopen:
            if l == b'"""\n':
                # end of docstring
                if lno <= 4:
                    yield lno+c, "missing module name in docstring"
                break

            if l != b"\n" and l[:4] != b'    ' and docopen:
                yield lno+c, "missing correct docstring indentation"

            if lno == 2:
                # if not in package, don't check the module name
                modname = fn[:-3].replace('/', '.').replace('.__init__', '')
                while modname:
                    if l.lower()[4:-1] == bytes(modname):
                        break
                    modname = '.'.join(modname.split('.')[1:])
                else:
                    yield 3, "wrong module name in docstring heading"
                modnamelen = len(l.strip())
            elif lno == 3:
                if l.strip() != modnamelen * b"~":
                    yield 4, "wrong module name underline, should be ~~~...~"

    else:
        yield 0, "missing end and/or start of docstring..."

    # check for correct copyright
    copyright = llist[-3:-2]
    if not copyright or not copyright_re.match(copyright[0]):
        yield 0, "no correct copyright info"

    # check for correct license fields
    license = llist[-2:-1]
    if not license or not license_re.match(license[0]):
        yield 0, "no correct license info"



@checker('.py', '.html', '.rst')
def check_whitespace_and_spelling(fn, lines):
    for lno, line in enumerate(lines):
        if b"\t" in line:
            yield lno+1, "OMG TABS!!!"
        if line[:-1].rstrip(b' \t') != line[:-1]:
            yield lno+1, "trailing whitespace"
        if ((b'XXX' in line) and                            # ALLOW-MISSPELLING
            (b'ALLOW-MISSPELLING' not in line)):
            yield lno+1, '"XXX" used'                       # ALLOW-MISSPELLING
        for word in misspellings:
            if ((word in line.lower()) and
                (b'ALLOW-MISSPELLING' not in line) and
                (b'autodoc' not in line)):
                yield lno+1, '"%s" used' % word


bad_tags = [b'<u>', b'<s>', b'<strike>', b'<center>', b'<font']

@checker('.html')
def check_xhtml(fn, lines):
    for lno, line in enumerate(lines):
        for bad_tag in bad_tags:
            if bad_tag in line:
                yield lno+1, "used " + bad_tag


def main(argv):
    global verbose
    global llength

    parser = OptionParser(usage='Usage: %prog [-v] [-l linelength] [-i ignorepath]* [path]')
    parser.add_option('-v', '--verbose', dest='verbose', default=False,
                      action='store_true')
    parser.add_option('-l', '--linelength', type="int", dest='llength', default=90)
    parser.add_option('-i', '--ignore-path', dest='ignored_paths',
                      default=[], action='append')
    options, args = parser.parse_args(argv[1:])

    if len(args) == 0:
        path = '.'
    elif len(args) == 1:
        path = args[0]
    else:
        print(args)
        parser.error('No more then one path supported')

    verbose = options.verbose
    llength = options.llength

    ignored_paths = set(abspath(p) for p in options.ignored_paths)

    num = 0
    out = StringIO()

    # if it is a single file, process assuming it is part of the package
    if os.path.isfile(path):
        fn = path
        if fn[:2] == './': fn = fn[2:]

        ext = splitext(fn)[1]
        checkerlist = checkers.get(ext, None)

        if (not (abspath(fn) in ignored_paths)) and checkerlist:
            if verbose:
                print("Checking %s..." % fn)

            try:
                f = open(fn, 'rb')
                try:
                    lines = list(f)
                finally:
                    f.close()
            except (IOError, OSError) as err:
                print("%s: cannot open: %s" % (fn, err))
                sys.exit(-1)

            for i, line in enumerate(lines):
                lines[i] = line.replace('\r\n','\n')

            for checker in checkerlist:
                for lno, msg in checker(fn, lines):
                    print("%s:%d: %s" % (fn, lno, msg), file=out)
                    num += 1

    else: # traverse the directory path
        for root, dirs, files in os.walk(path):
            for vcs_dir in ['.svn', '.hg', '.git']:
                if vcs_dir in dirs:
                    dirs.remove(vcs_dir)
            if abspath(root) in ignored_paths:
                del dirs[:]
                continue
            in_check_pkg = root.startswith('./viol')
            for fn in files:

                fn = join(root, fn)
                if fn[:2] == './': fn = fn[2:]

                if abspath(fn) in ignored_paths:
                    continue

                ext = splitext(fn)[1]
                checkerlist = checkers.get(ext, None)
                if not checkerlist:
                    continue

                if verbose:
                    print("Checking %s..." % fn)

                try:
                    f = open(fn, 'rb')
                    try:
                        lines = list(f)
                    finally:
                        f.close()
                except (IOError, OSError) as err:
                    print("%s: cannot open: %s" % (fn, err))
                    num += 1
                    continue

                for i, line in enumerate(lines):
                    lines[i] = line.replace('\r\n','\n')

                for checker in checkerlist:
                    if not in_check_pkg and checker.only_pkg:
                        continue
                    for lno, msg in checker(fn, lines):
                        print("%s:%d: %s" % (fn, lno, msg), file=out)
                        num += 1
    if verbose:
        print()
    if num == 0:
        print("No errors found.")
    else:
        print(out.getvalue().rstrip('\n'))
        print("%d error%s found." % (num, num > 1 and "s" or ""))
    return int(num > 0)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
