# -*- coding: utf-8 -*-
"""
    invx.__main__
    ~~~~~~~~~~~~~

    The invx utility main entry point

    :copyright: Copyright (c) 2018 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

from __future__ import absolute_import

import os
import sys

# If we are running from a wheel, add the wheel to sys.path
# This allows the usage python invx-*.whl/invx install invx-*.whl
if __package__ == '':
    # __file__ is invx-*.whl/invx/__main__.py
    # first dirname call strips of '/__main__.py', second strips off '/invx'
    # Resulting path is the name of the wheel itself
    # Add that to sys.path so we can import invx
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)

import invx     # noqa

__author__      = 'John Fogelin'
__email__       = 'john@bitharmony.com'

try:
    _dist = get_distribution('invx')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, 'invx')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = 'version unknown: install invx with setup.py'
else:
    __version__ = _dist.version

if __name__ == '__main__':
    sys.exit(invx.main())
