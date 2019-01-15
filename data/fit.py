#!/usr/bin/env python

import os
import numpy as np
from scipy import optimize
from scipy.special import fresnel
from scipy.spatial import distance
import matplotlib.pyplot as plt
import math
from math import ceil, log, sqrt

from svgpathtools import Path, Line, CubicBezier, parse_path, svg2paths, svg2paths2
from svgpathtools import wsvg, disvg, bezier_point, bezier2polynomial, kinks, smoothed_path
from timeit import default_timer as timer
from time import sleep

def f(t, a):
    ss, cc = fresnel(t)
    return complex(a*ss, a*cc)

a = 100
t = np.linspace(0, 2.1, 100)
y = f(t, a)

tn = np.linspace(0, 2.1, 200)

a0 = 40

popt, pcov = optimize.curve_fit(f, t, y, p0=a0)
print popt

plt.plot(x, y, 'or')
plt.plot(tn, f(tn, popt))
plt.show()

