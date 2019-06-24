# -*- coding: utf-8 -*-
"""
    viol.__main__
    ~~~~~~~~~~~~~

    The viol utility entry point for automatic python -m viol execution

    :copyright: Copyright (c) 2019 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""

# pylint: disable=no-value-for-parameter

from __future__ import absolute_import
import sys
from viol.cmds import viol_main

if __name__ == '__main__':
    sys.exit(viol_main())
