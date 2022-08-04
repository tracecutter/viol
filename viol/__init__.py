# -*- coding: utf-8 -*-
"""
    viol
    ~~~~

    viol - viol instrument design utility

    :copyright: Copyright (c) 2021 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""
import os
import sys
from pkg_resources import get_distribution, DistributionNotFound

# The version is set at build time and is in sync with setup.py and the docs conf.py
__author__      = 'John Fogelin'
__email__       = 'john@bitharmony.com'

# If we are running from a wheel, add the wheel to sys.path
# This allows the usage python viol-*.whl/viol install viol-*.whl
if __package__ == '':
    # __file__ is viol-*.whl/viol/__main__.py
    # first dirname call strips of '/__main__.py', second strips off '/viol'
    # Resulting path is the name of the wheel itself
    # Add that to sys.path so we can import viol
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)

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
