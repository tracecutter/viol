# -*- coding: utf-8 -*-
"""
    viol.__init__
    ~~~~~~~~~~~~~

    viol - viol design utility main entry point

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

# If we are running from a wheel, add the wheel to sys.path
# This allows the usage python viol-*.whl/viol install viol-*.whl
if __package__ == '':
    # __file__ is viol-*.whl/viol/__main__.py
    # first dirname call strips of '/__main__.py', second strips off '/viol'
    # Resulting path is the name of the wheel itself
    # Add that to sys.path so we can import viol
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)

import logging
import logging.config
import click

from pkg_resources      import get_distribution, DistributionNotFound

from viol               import cmds

# pylint: disable=E1103

# Disable click warning for importing unicode_literals in python 2
click.disable_unicode_literals_warning = True

# The version is set at build time and is in sync with setup.py and the docs conf.py
__author__      = 'John Fogelin'
__email__       = 'john@bitharmony.com'

try:
    _dist = get_distribution('viol')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, 'viol')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = 'version unknown: install viol with setup.py'
else:
    __version__ = _dist.version


@click.group(cls=cmds.make_commands('viol.cmds'))
@click.version_option(__version__, '--version', '-v')
@click.option('--outfmt', type=click.Choice(['json', 'yaml', 'csv']))
@click.option('--debug/--no-debug',
              help='Sets logging level to debug',
              is_flag=True, default=False)
@click.pass_context
def main(ctx, outfmt, debug):
    """viol command line interface"""
    ctx.obj = {}
    ctx.obj['logging.debug'] = False

    if outfmt:
        cmds.OUTPUT_FORMAT = outfmt

    #XXX Add logging facility from pip

if __name__ == '__main__':
    sys.exit(main())
