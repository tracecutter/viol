# -*- coding: utf-8 -*-
"""
    viol.__main__
    ~~~~~~~~~~~~~

    The viol utility entry point for automatic python main execution

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

from __future__ import absolute_import

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

import viol     # noqa

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

if __name__ == '__main__':
    sys.exit(viol.main())
