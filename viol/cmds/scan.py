# -*- coding: utf-8 -*-
"""
    viol.cmds.scan
    ~~~~~~~~~~~~~~

    Viol scanning and curve fitting utility.

    :copyright: Copyright (c) 2021 Bit Harmony Ltd. All rights reserved. See AUTHORS.
    :license: PROPRIETARY, see LICENSE for details.
"""


import tempfile
#import json
import jsonpickle
import math
import cmath
import numpy as np
import matplotlib.pyplot as plt

#from time import sleep
#from timeit import default_timer as timer
from matplotlib.figure import SubplotParams
from scipy.special import fresnel
from scipy.optimize import minimize_scalar
from io import BytesIO
from subprocess import Popen, PIPE, STDOUT
from PIL import Image
from svgpathtools import Path, Line, CubicBezier, svg2paths2, wsvg, disvg
from svgpathtools import bezier_point, bezier2polynomial, polynomial2bezier, bpoints2bezier, split_bezier
from svgpathtools.polytools import polyroots01

from viol.lib.util_str import str_instance

import logging
import click


logger = logging.getLogger(__name__)


class Clothoid:
    """A clothoid (Euler's Sprial, Cornu Spiral, Fresnel Integral) class.  The clothoid can be
    scaled, rotated, and shifted to a new origin.  The clothoid can be flipped to turn clockwise or
    counterclockwise.  The clothoid can begin at T0 (other than 0.0) to start with a curvature greater
    than 0.  If this is the case, the rotation is increased so the clothoid points the same direction as
    if T0 was 0 (in the direction of the parameter rotation)."""
    def __init__(self, scale=1, rotation=0, origin=(0, 0), clockwise=True, T0=0.0, T=2.1):
        self.T0         = T0
        self.T          = T
        self.scale      = scale
        self.origin     = origin
        self.clockwise  = clockwise
        twist = (1, -1)[bool(self.clockwise)]
        # adjust rotation based upon tangent at fresnel(T0)
        self.rotation   = (rotation - twist *
                           math.atan2(math.sin((cmath.pi * T0 ** 2) / 2), math.cos((cmath.pi * T0 ** 2) / 2)))

    def __repr__(self):
        return(str_instance(self))

    def vectors(self):
        t = np.linspace(self.T0, self.T, 1000)
        ss, cc = fresnel(t)                 # crank out the sin and cos vectors of the unit euler curve (fresnel integral)
        ss = ss - fresnel(self.T0)[0]       # shift the curve origin to T0
        cc = cc - fresnel(self.T0)[1]       # shift the curve origin to T0
        twist = (1, -1)[bool(self.clockwise)]
        svec = (((self.scale * cc * math.cos(twist * self.rotation)) -
                (self.scale * ss * math.sin(twist * self.rotation))) +
                self.origin[0])
        cvec = (twist * ((self.scale * cc * math.sin(twist * self.rotation)) +
                (self.scale * ss * math.cos(twist * self.rotation))) +
                self.origin[1])
        return svec, cvec

    def p(self, t=0):
        return (complex(self.x(t), self.y(t)))

    def x(self, t=0):
        ss, cc = fresnel(t)                 # crank out the sin and cos vectors of the unit euler curve (fresnel integral)
        ss = ss - fresnel(self.T0)[0]       # shift the curve origin to T0
        cc = cc - fresnel(self.T0)[1]       # shift the curve origin to T0
        twist = (1, -1)[bool(self.clockwise)]
        return (((self.scale * cc * math.cos(twist * self.rotation)) -
                (self.scale * ss * math.sin(twist * self.rotation))) +
                self.origin[0])

    def y(self, t=0):
        ss, cc = fresnel(t)                 # crank out the sin and cos vectors of the unit euler curve (fresnel integral)
        ss = ss - fresnel(self.T0)[0]       # shift the curve origin to T0
        cc = cc - fresnel(self.T0)[1]       # shift the curve origin to T0
        twist = (1, -1)[bool(self.clockwise)]
        return (twist * ((self.scale * cc * math.sin(twist * self.rotation)) +
                (self.scale * ss * math.cos(twist * self.rotation))) +
                self.origin[1])

    def tangent(self, t=0):
        # XXX is t relative to self.T0
        # XXX check that twist is implemented correctly
        cc = math.cos((cmath.pi / 2) * t ** 2)
        ss = math.sin((cmath.pi / 2) * t ** 2)
        twist = (1, -1)[bool(self.clockwise)]
        x = (((cc * math.cos(twist * self.rotation)) -
              (ss * math.sin(twist * self.rotation))))
        y = twist * (((cc * math.sin(twist * self.rotation)) +
              (ss * math.cos(twist * self.rotation))))
        # XXX shoud tangent be shifted to origin(self.T0)?
        return complex(x, y)

    def closest_t(self, p, max_t=2.2):
        """Return t on the clothoid closest to p."""
        f = lambda t: np.linalg.norm(self.p(t) - p)
        return minimize_scalar(f, bounds=(0, max_t), method='bounded', options={'xatol': 1e-5, 'disp': 0}).x

    def plot(self, plot, color='r-'):
        ss, cc = self.vectors()
        plot.plot(ss, cc, color, linewidth=1)


class Point:
    """A basic point."""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return(str_instance(self))

    def plot(self, plot, color='b^'):
        plot.plot([self.x], [self.y], color)


class POI:
    """A point of interest."""
    def __init__(self, path, T=0, p=None, label=None):
        self.path = path    # XXX Carrying a reference to the path make the JSON pickle large!
        self.label = label
        if p is not None:
            self.T = path_closest_t(path, p)
        else:
            self.T = T

    def __repr__(self):
        return(str_instance(self))

    def p(self):
        return self.path.point(self.T)

    def x(self):
        return self.path.point(self.T).real

    def y(self):
        return self.path.point(self.T).imag

    def tangent(self):
        try:
            tangent = self.path.unit_tangent(self.T)
        except AssertionError:
            tangent = self.path.unit_tangent(self.T - .01)
        return tangent

    def plot(self, plot, color='b^'):
        plot.plot([self.x()], [self.y()], color)

    def plot_t(self, plot, color='b--'):
        plot.plot([self.T, self.T], [0, 1], color)
        if self.label is not None:
            plot.annotate(self.label, xy=(self.T, 0), xytext=(self.T, 0), rotation=90,
                          verticalalignment='bottom', horizontalalignment='center')

    def plot_tangent(self, plot, color='b--'):
        Tangent(self.path, self.T).plot(plot, color)


class Tangent:
    """A unit tangent on a path at T"""
    def __init__(self, path, T=0, mag=50):
        try:
            tan = path.unit_tangent(T)
        except AssertionError:
            tan = path.unit_tangent(T + .001)
        self.start = path.point(T) - mag * tan
        self.end = path.point(T) + mag * tan

    def __repr__(self):
        return(str_instance(self))

    def plot(self, plot, color='g-'):
        plot.plot([self.start.real, self.end.real], [self.start.imag, self.end.imag], color)


class Bout:
    """A bout from the POI left to the POI right"""
    def __init__(self, left, right, label=None):
        self.left = left
        self.right = right
        self.label = label

    def __repr__(self):
        return(str_instance(self))

    def plot(self, plot, color='r-'):
        plot.plot([self.left.x(), self.right.x()], [self.left.y(), self.right.y()], color)

    def plot_t(self, plot, color='b--'):
        plot.plot([self.left.T, self.left.T], [0, 1], color)
        plot.plot([self.right.T, self.right.T], [0, 1], color)
        if self.label is not None:
            plot.annotate(self.label + "L", xy=(self.left.T, 0), xytext=(self.left.T, 0), rotation=90,
                          verticalalignment='bottom', horizontalalignment='center')
            plot.annotate(self.label + "R", xy=(self.right.T, 0), xytext=(self.right.T, 0), rotation=90,
                          verticalalignment='bottom', horizontalalignment='center')

    def plot_tangent(self, plot, color='b--'):
        self.left.plot_tangent(plot, color)
        self.right.plot_tangent(plot, color)


class Corner:
    """A corner POI."""
    def __init__(self, poi):
        self.poi = poi

    def __repr__(self):
        return(str_instance(self))

    def plot(self, plot, color='b^'):
        self.poi.plot(plot, color)


class CL:
    """A centerline from the POI b(ottom) to the POI t(op)"""
    def __init__(self, path, label=None):
        self.top_left = POI(path, T=0.0)
        self.top_right = POI(path, T=1.0)
        self.bot = POI(path, p=complex(self.top_left.x(), 0))
        self.label = label

    def __repr__(self):
        return(str_instance(self))

    def plot(self, plot, color='r-'):
        plot.plot([self.bot.x(), self.top_left.x()], [self.bot.y(), self.top_left.y()], color)

    def plot_t(self, plot, color='b--'):
        plot.plot([self.top_left.T, self.top_left.T], [0, 1], color)
        plot.plot([self.top_right.T, self.top_right.T], [0, 1], color)
        plot.plot([self.bot.T, self.bot.T], [0, 1], color)
        if self.label is not None:
            plot.annotate(self.label + "TL", xy=(self.top_left.T, 0), xytext=(self.top_left.T, 0), rotation=90,
                          verticalalignment='bottom', horizontalalignment='center')
            plot.annotate(self.label + "TR", xy=(self.top_right.T, 0), xytext=(self.top_right.T, 0), rotation=90,
                          verticalalignment='bottom', horizontalalignment='center')
            plot.annotate(self.label + "B", xy=(self.bot.T, 0), xytext=(self.bot.T, 0), rotation=90,
                          verticalalignment='bottom', horizontalalignment='center')

    def plot_tangent(self, plot, color='b--'):
        self.top_left.plot_tangent(plot, color)
        self.bot.plot_tangent(plot, color)


class Bouts:
    """A set of viola body bouts."""
    def __init__(self, path, bout_tol=0.1):
        # We sweep around all segements of the viol body and nominate all possible bout features
        # to bouts[] based on a vertical unit tangent ie. (0, pi)

        # we need a vectorized function to find the tangent of a curve XXX  Really?!
        vec_f_tan = np.vectorize(lambda t: seg.unit_tangent(t))
        seg = path[0]
        seg_prev_tan = np.average(vec_f_tan(np.linspace(0.0, 1.0, 10)))

        segs = []
        for ix, seg in enumerate(path):
            seg_tan = np.average(vec_f_tan(np.linspace(0.0, 1.0, 10)))
            d_real = max(seg_tan.real, seg_prev_tan.real) - min(seg_tan.real, seg_prev_tan.real)
            d_imag = max(seg_tan.imag, seg_prev_tan.imag) - min(seg_tan.imag, seg_prev_tan.imag)
            if (abs(seg_tan.real) < bout_tol) and (abs(seg_tan.imag) > (1.0 - bout_tol)):
                segs.append(ix)
            seg_prev_tan = seg_tan

        top = path.point(0).imag

        # XXX assumes the bouts occur in the body terciles

        # Find the upper left and right bout points in upper third of scan

        start, end = path_extrema_t(path, segs, top * 2.0 / 3.0, top)
        self.upper = Bout(POI(path, start), POI(path, end), label="Bout_U")

        #T = path_find_slope(path, 0, .18, phi=-cmath.pi/2.0)
        #seg, t = path.T2t(T)
        #print "XXX:", T, seg, t
        #print "YYY:", path_extrema_t(path, [seg], 0, top)

        #start, end = path_extrema_t(path, segs, top*2.0/3.0, top)

        #viola.body.inspect(path_find_slope(path, .2, .3, phi=-cmath.pi/2.0))
        #viola.body.inspect(path_find_slope(path, .35, .5, phi=-cmath.pi/2.0))

        # Find the lower left and right bout points
        start, end = path_extrema_t(path, segs, 0.0, top * 1.0 / 3.0)
        self.lower = Bout(POI(path, start), POI(path, end), label="Bout_L")

        # Find the middle left and right bout points
        start, end = path_extrema_t(path, segs, top * 1.0 / 3.0, top * 2.0 / 3.0, reverse=True)
        self.middle = Bout(POI(path, start), POI(path, end), label="Bout_M")

    def __repr__(self):
        return(str_instance(self))

    def plot(self, plot, color='r-'):
        self.upper.plot(plot, color)
        self.middle.plot(plot, color)
        self.lower.plot(plot, color)

    def plot_t(self, plot, color='b--'):
        self.upper.plot_t(plot, color)
        self.middle.plot_t(plot, color)
        self.lower.plot_t(plot, color)

    def plot_tangent(self, plot, color='b--'):
        self.upper.plot_tangent(plot, color)
        self.middle.plot_tangent(plot, color)
        self.lower.plot_tangent(plot, color)


class Corners:
    """A set of viola body corners."""
    def __init__(self, path, bouts, corner_curve_tol=0.1):
        # we need a vectorized function to find the tangent of a curve XXX  Really?!
        vec_f_tan = np.vectorize(lambda t: seg.unit_tangent(t))

        corners = []
        seg = path[0]
        seg_prev_tan = np.average(vec_f_tan(np.linspace(0.0, 1.0, 10)))

        # We sweep around all segements of the viol body and nominate all possible corner features to corners[] based on
        # significant changes in direction. Corners have segment to segment jump of curvature > .5.
        for ix, seg in enumerate(path):
            seg_tan = np.average(vec_f_tan(np.linspace(0.0, 1.0, 10)))
            d_real = max(seg_tan.real, seg_prev_tan.real) - min(seg_tan.real, seg_prev_tan.real)
            d_imag = max(seg_tan.imag, seg_prev_tan.imag) - min(seg_tan.imag, seg_prev_tan.imag)
            if (abs(d_real) + abs(d_imag) > corner_curve_tol):
                corners.append(ix)
            seg_prev_tan = seg_tan

        # Now we bracket our search based on bout locales to determine the real corners

        # Find the lower corners
        bot = bouts.lower.left.y()
        top = bouts.middle.left.y()
        start, end = path_extrema_t(path, corners, bot, top)
        self.lower_left = POI(path, start, label="Corner_LL")
        self.lower_right = POI(path, end, label="Corner_LR")

        # Find the upper corners
        bot = bouts.middle.left.y()
        top = bouts.upper.left.y()
        start, end = path_extrema_t(path, corners, bot, top)
        self.upper_left = POI(path, start, label="Corner_UL")
        self.upper_right = POI(path, end, label="Corner_UR")

    def __repr__(self):
        return(str_instance(self))

    def plot(self, plot, color='b^'):
        self.upper_left.plot(plot, color)
        self.lower_left.plot(plot, color)
        self.lower_right.plot(plot, color)
        self.upper_right.plot(plot, color)

    def plot_t(self, plot, color='b--'):
        self.upper_left.plot_t(plot, color)
        self.lower_left.plot_t(plot, color)
        self.lower_right.plot_t(plot, color)
        self.upper_right.plot_t(plot, color)

    def plot_tangent(self, plot, color='b--'):
        self.upper_left.plot_tangent(plot, color)
        self.lower_left.plot_tangent(plot, color)
        self.upper_right.plot_tangent(plot, color)
        self.lower_right.plot_tangent(plot, color)


class Turns:
    """A set of viola turning points where arc reverses (ie. clockwise to counter clockwise)."""
    def __init__(self, path, bouts, corners):
        # Now we bracket our search based on bouts and corners to find the turns (change of direction)
        # This occurs at the point where the tangent is minimally orthogonal to the x axis

        f = lambda t: abs(path.unit_tangent(t).imag / path.unit_tangent(t).real)

        T0 = bouts.upper.left.T
        T1 = corners.upper_left.T
        T = minimize_scalar(f, bounds=(T0, T1), method='bounded', options={'xatol': 1e-5, 'disp': 0}).x
        self.upper_left = POI(path, T, label="Turn_UL")

        T0 = corners.lower_left.T
        T1 = bouts.lower.left.T
        T = minimize_scalar(f, bounds=(T0, T1), method='bounded', options={'xatol': 1e-5, 'disp': 0}).x
        self.lower_left = POI(path, T, label="Turn_LL")

        T0 = bouts.lower.right.T
        T1 = corners.lower_right.T
        T = minimize_scalar(f, bounds=(T0, T1), method='bounded', options={'xatol': 1e-5, 'disp': 0}).x
        self.lower_right = POI(path, T, label="Turn_LR")

        T0 = corners.upper_right.T
        T1 = bouts.upper.right.T
        T = minimize_scalar(f, bounds=(T0, T1), method='bounded', options={'xatol': 1e-5, 'disp': 0}).x
        self.upper_right = POI(path, T, label="Turn_UR")

    def __repr__(self):
        return(str_instance(self))

    def plot(self, plot, color='b^'):
        self.upper_left.plot(plot, color)
        self.lower_left.plot(plot, color)
        self.lower_right.plot(plot, color)
        self.upper_right.plot(plot, color)

    def plot_t(self, plot, color='b--'):
        self.upper_left.plot_t(plot, color)
        self.lower_left.plot_t(plot, color)
        self.lower_right.plot_t(plot, color)
        self.upper_right.plot_t(plot, color)

    def plot_tangent(self, plot, color='b--'):
        self.upper_left.plot_tangent(plot, color)
        self.lower_left.plot_tangent(plot, color)
        self.upper_right.plot_tangent(plot, color)
        self.lower_right.plot_tangent(plot, color)


class Body:
    """A Viola subcomponent class of the instrument body geometry, features, and attributes."""
    def __init__(self):
        self.clothoids = []
        self.guesses = []
        self.inspects = []
        self.highlights = []
        self.path = None
        self.path_attributes = None
        self.pathsvg_attributes = None
        self.feature_bbox = []
        self.feature_centerline = None
        self.feature_bouts = None
        self.feature_corners = None
        self.feature_turns = None
        self.feature_45_upper_left = None
        self.feature_45_lower_left = None
        self.feature_45_lower_right = None
        self.feature_45_upper_right = None
        self.feature_45_upper_left_tangent = None
        self.feature_45_lower_left_tangent = None
        self.feature_45_lower_right_tangent = None
        self.feature_45_upper_right_tangent = None

    def __repr__(self):
        return(str_instance(self))

    def __str__(self):
        # A terser description of only human readable features.
        # Generator to filter which properties to show.
        # This example excludes properties prefixed with "_" and methods.
        def filter_props(obj):
            props = sorted(obj.__dict__.keys())
            for prop in props:
                if not callable(prop) and prop.startswith('feature'):
                    yield (prop, getattr(obj, prop))
        prop_tuples = filter_props(self)
        result = "<" + self.__class__.__name__ + "("
        for prop in prop_tuples:
            result += prop[0].__str__() + "="
            # Stylize (if desired) the output based on the type.
            # This example shortens floating point values to three decimal places.
            if isinstance(prop[1], float):
                result += "{:.3f}, ".format(prop[1])
            else:
                result += prop[1].__repr__() + ", "

        result = result[:-2]
        result += ")>"
        return result

    def scan(self, imageFile, dpi=300, threshold=205, despeckle=10):
        img = Image.open(imageFile)
        img = img.convert(mode="L")

        # convert from input dots per inch to 100 dots per cm (.1mm resolution)
        resize = 2540.0 / (10.0 * dpi)
        w, h = img.size
        img = img.resize((int(w * resize), int(h * resize)), Image.LANCZOS)
        img = img.point(lambda x: 0 if x < threshold else 255, '1')

        # XXX one could preview the threshold result with img.show()

        # convert the image to a bitmap memory file for input to potrace
        bmp = BytesIO()
        img.save(bmp, format='BMP')
        bmp.seek(0)

        # execute potrace as a subprocess filter stdin to stdout
        p = Popen(['potrace', '-s', '-t', str(despeckle)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        svg_tmp = tempfile.NamedTemporaryFile(mode='w')
        svg_tmp.write(p.communicate(input=bmp.read())[0].decode())
        svg_tmp.flush()

        # parse the svg file to extract the cubic bezier curve paths
        paths, attributes, svg_attributes = svg2paths2(svg_tmp.name)
        svg_tmp.close()

        # XXX assume here that the longest path is the body we want, and rest is clutter
        # we could try different threshold values until a reasonble path count is found.
        # we could also detect split long paths and join them together
        path = paths[0]
        for p in paths:
            if p.length() > path.length():
                path = p

        # body path traces both outside and inside the trace... we only want inside trace
        # XXX we assume here that potrace closes the outside curve before starting the
        # inside curve.  It is probably more defensive to chose the first segment endpoint (after t > 0.1)
        # that has the closest Euclidean distance to the starting point.
        # an assumption that potrace starts the path at top most part of viola has probably
        # snuck into the code somewhere, so it would be good check and correct those conditions.

        endpoints = [ix for ix, seg in enumerate(path) if seg.point(1) == path.point(0)]
        del(path[endpoints[0] + 1:])

        # check that the viola body path is closed
        assert(path.iscontinuous())

        # normalize the path for (0, 0) at the centerline of the bottom of the instrument
        # XXX A proper centerline would be to consider vertical extremi, or average(x) for all x,
        # or svgpathtools.path.point(0.5). It also may be tilted, so a rotation is required.

        xmin, xmax, ymin, ymax = path.bbox()                         # use a bounding box to determine x, y extremi
        xshift = path.point(0.0).real                                # T=0 appears to find top most point
        scale = 1000.0 / 10.0 ** (math.ceil(np.log10(ymax - ymin)))  # calculate scaling factor for pixel == 0.1mm
        path = path.translated(complex(-xshift, -ymin))              # complex translation vector
        path = path.scaled(scale)                                    # scale path to 10 pixels/mm (curves get detached)
        for ix, seg in enumerate(path[:-1]):
            seg.end = path[ix + 1].start                            # reattach curves so path.iscontinuous()
        path[-1].end = path[0].start

        self.path = path
        self.path_attributes = attributes
        self.pathsvg_attributes = svg_attributes                # XXX Seems not to like svg version of 1.0
        self.feature_bbox = path.bbox()                         # establish a bounding box around whole body
        self.path = path_smooth(self.path)                      # smooth the path
        self.path = path_compress(self.path)                    # compress the path
        self.path = path_flatten_top(self.path)                 # make tangent horizotal at top
        self.path = path_flatten_bottom(self.path)              # make tangent horizotal at bottom
        self.features_find()                                    # extract the path features
        self.clothoids_find()                                   # build a clothoid model of the body

    def features_find(self, bout_tol=0.1, corner_curve_tol=1.0):
        """Use properties of a Viola to establish bout locations and widths, corner locations, etc."""
        # establish the viol centerline
        self.feature_centerline = CL(self.path, label="CL_")
        self.feature_bouts = Bouts(self.path, bout_tol)                                  # find the bouts
        self.feature_corners = Corners(self.path, self.feature_bouts, corner_curve_tol)  # find the corners
        self.feature_turns = Turns(self.path, self.feature_bouts, self.feature_corners)  # find the turns

    def clothoids_find(self):
        """Define a set of clothoids based on path features."""
        # Now we search for four clothoid joins to yield best curve fit
        # XXX The joins should be based on curvature minima and not arbitrarily at 45 degrees.

        T0 = 0.015
        T1 = self.feature_bouts.upper.left.T - 0.015
        T = path_find_slope(self.path, T0, T1, phi=-3.0 * cmath.pi / 4.0)
        self.feature_45_upper_left = POI(self.path, T, label="45_UL")

        T0 = self.feature_bouts.lower.left.T + 0.015
        T1 = self.feature_centerline.bot.T - 0.015
        T = path_find_slope(self.path, T0, T1, phi=-cmath.pi / 4.0)
        self.feature_45_lower_left = POI(self.path, T, label="45_LL")

        T0 = self.feature_centerline.bot.T + 0.015
        T1 = self.feature_bouts.lower.right.T - 0.015
        T = path_find_slope(self.path, T0, T1, phi=cmath.pi / 4.0)
        self.feature_45_lower_right = POI(self.path, T, label="45_LR")

        T0 = self.feature_bouts.upper.right.T + 0.015
        T1 = self.feature_centerline.top_right.T - 0.015
        T = path_find_slope(self.path, T0, T1, phi=3 * cmath.pi / 4.0)
        self.feature_45_upper_right = POI(self.path, T, label="45_UR")

        # XXX I can't think of an obvious way to make this less ugly! A global dictionary?!
        clist = [
            [self.feature_centerline.top_left, self.feature_45_upper_left],
            [self.feature_turns.upper_left, self.feature_45_upper_left],
            [self.feature_turns.upper_left, self.feature_corners.upper_left],
            [self.feature_bouts.middle.left, self.feature_corners.upper_left],
            [self.feature_bouts.middle.left, self.feature_corners.lower_left],
            [self.feature_turns.lower_left, self.feature_corners.lower_left],
            [self.feature_turns.lower_left, self.feature_45_lower_left],
            [self.feature_centerline.bot, self.feature_45_lower_left],
            [self.feature_centerline.bot, self.feature_45_lower_right],
            [self.feature_turns.lower_right, self.feature_45_lower_right],
            [self.feature_turns.lower_right, self.feature_corners.lower_right],
            [self.feature_bouts.middle.right, self.feature_corners.lower_right],
            [self.feature_bouts.middle.right, self.feature_corners.upper_right],
            [self.feature_turns.upper_right, self.feature_corners.upper_right],
            [self.feature_turns.upper_right, self.feature_45_upper_right],
            [self.feature_centerline.top_right, self.feature_45_upper_right]
        ]

        # iterate over every clothoid to construct
        for ix, points in enumerate(clist):
            p0, p1 = [points[0], points[1]]
            t0 = 0.0

            # the unit_tangent at the corners is wonky, so we trim back the curve to just short of corner
            if p1 in [self.feature_corners.upper_left, self.feature_corners.upper_right,
                      self.feature_corners.lower_left, self.feature_corners.lower_right]:
                adj = .003
            else:
                adj = 0

            if p0 is self.feature_bouts.middle.left:
                p0 = POI(self.path, T=0.2247112)
            #    t0 = (curvature == .012)
            #    XXX but curvature depends on scale!

            # calculate clothoid twist entry angle and determine if clockwise or anticlockwise twist
            rotation, clockwise  = phase_delta(p0, p1)
            # estimate the scale based on arclength of bezier path
            if p1.T > p0.T:
                arclen = self.path.length(p0.T, p1.T)
                tan = (cmath.phase(p1.path.unit_tangent(p1.T - adj)) + (2 * cmath.pi)) % (2 * cmath.pi)
            else:
                arclen = self.path.length(p1.T, p0.T)
                tan = (cmath.phase(-p1.path.unit_tangent(p1.T + adj)) + (2 * cmath.pi)) % (2 * cmath.pi)

            # how much additional twist after initial rotation required?
            phi = abs(phase_delta_min(rotation, tan))

            # solve for the t on a clothoid that twists phi degrees and scale up to match bezier arclen
            t = math.sqrt((2 * phi) / cmath.pi)
            scale = arclen / t

            fmt = "Cl{:2d}: t0:{:.2f} t1:{:.2f} rot:{:6.2f} phi:{:6.2f} arc:{:6.2f} scale:{:6.2f} eul_t:{:.2f}"
            print(fmt.format(ix + 1, p0.T, p1.T, math.degrees(rotation), math.degrees(phi), arclen, scale, t))

            #cl = Clothoid(scale, rotation, (p0.x(), p0.y()), clockwise)
            #self.clothoids.append(cl)

            tn = t

            for i in range(0, 3):
                cl = Clothoid(scale, rotation, (p0.x(), p0.y()), clockwise, T0=t0, T=tn)
                #cl = Clothoid(scale, rotation, (p0.x(), p0.y()), clockwise, T0=t0, T=2.5)
                # XXX this should respect is)corner from above!
                tn = cl.closest_t(p1.p(), max_t=tn)
                ph1 = cmath.phase(p1.p() - p0.p())
                ph2 = cmath.phase(cl.p(t) - p0.p())

                #print ("p1:", p1)
                #print ("t, p(t):", t, cl.p(t))
                #print ("ph1, ph2, delta, min_delta_degrees:", ph1, ph2, ph1 - ph2, phase_delta_min(ph1, ph2))
                #print ("rotation", rotation, math.degrees(rotation))
                #self.guesses.append(Point(cl.x(tn), cl.y(tn)))
                #self.clothoids.append(cl)
                rotation = rotation + (ph1 - ph2)

            # evaluate clothoid results
            path_compare(self.path, p0.T, p1.T, cl, cl.T0, cl.T, nodes=10)

            self.clothoids.append(cl)


    def inspect (self, T=0):
        self.inspects.append(POI(self.path, T))

    def plot (self, plot=None, plot_tangents=False):
        """Plot a viola using matplotlib.  Note this does not display the plot."""
        # XXX This function needs color arguments
        # XXX This function needs plot size and axis arguments
        # XXX This function needs an "exclude" features list
        # XXX This function needs an "include" features list
        if plot is None:
            plt.figure(figsize=(6, 8.4))
            plt.axis([-150, 150, 0, 420])
            plot = plt
        # Use a self referential string search to establish plottable features.
        features = [(key) for key, value in self.__dict__.items() if key.startswith("feature")]
        for feature in features:
            try:
                getattr(self, feature).plot(plot)
                if plot_tangents:
                    getattr(self, feature).plot_tangent(plot)
            except AttributeError:
                pass

        # Plot the clothoids (if any)
        for clothoid in self.clothoids:
            clothoid.plot(plot)

        # Plot the guesses

        for guess in self.guesses:
            guess.plot(plot)

        # Plot inspection points

        for inspect in self.inspects:
            inspect.plot(plot)

        # Plot body path by digitizing the bezier curve(s) with 5000 points
        x, y = list(zip(*[(self.path.point(T).real, self.path.point(T).imag) for T in np.linspace(0.0, 1.0, 5000)]))
        plot.plot(x, y, 'b-')

        # Highlight segments in highlights list
        for seg in self.highlights:
            T0 = self.path.t2T(seg, 0)
            T1 = self.path.t2T(seg, 1)
            x, y = list(zip(*[(self.path.point(T).real, self.path.point(T).imag) for T in np.linspace(T0, T1, 100)]))
            plot.plot(x, y, 'g-')

        return plot

    def plot_curvature (self, plot=None):
        if plot is None:
            fig, plot = plt.subplots(figsize=(12, 6), subplotpars=SubplotParams(bottom=.2))
            plot.axis([0, 1, 0.05, 0])
            plot.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True)
            plot2 = plot.twinx()
            plot2.axis([0, 1, 0, 250])
            plot2.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

        x = []
        y = []
        #sweep T in [0, T+.02, T+.04]
        delta = 0.02
        for t0 in np.linspace(0.0, 1.0 - (2 * delta), 500):
            x.append(t0 + delta)
            y.append(path_curvature(t0, self.path))
        plot.plot(x, y, 'r-')

        x = []
        y = []
        #sweep T in [0, 1]
        for t in np.linspace(0.0, .5, 250):
            x.append((.5 - abs(self.path.point(t).imag) / (2 * 388)))
            y.append(abs(self.path.point(t).real))
        for t in np.linspace(0.5, 1, 250):
            x.append((.5 + abs(self.path.point(t).imag) / (2 * 388)))
            y.append(abs(self.path.point(t).real))
        plot2.plot(x, y, 'b-')

        # Use a self referential string search to establish plottable features.
        features = [(key) for key, value in self.__dict__.items() if key.startswith("feature")]
        for feature in features:
            try:
                getattr(self, feature).plot_t(plot)
            except AttributeError:
                pass

        return plot


class Viola:
    """An instrument class of the components of an instrument in the viol family."""
    def __init__(self):
        self.body = Body()

    def __repr__(self):
        return(str_instance(self))

    def __str__(self):
        # A terser description of only human readable features.
        # Generator to filter which properties to show.
        # This example excludes properties prefixed with "_" and methods.
        def filter_props(obj):
            props = sorted(obj.__dict__.keys())
            for prop in props:
                if not callable(prop) and prop[0] != "_":
                    yield (prop, getattr(obj, prop))
        prop_tuples = filter_props(self)
        result = "<" + self.__class__.__name__ + "("
        for prop in prop_tuples:
            result += prop[0].__str__() + "="
            # Stylize (if desired) the output based on the type.
            # This example shortens floating point values to three decimal places.
            if isinstance(prop[1], float):
                result += "{:.3f}, ".format(prop[1])
            else:
                result += prop[1].__str__() + ", "

        result = result[:-2]
        result += ")>"
        return result

    def body_scan(self, imageFile, dpi=300, threshold=205, despeckle=10):
        self.body.scan(imageFile, dpi, threshold, despeckle)

    def plot(self, plot=None, plot_tangents=False):
        self.body.plot(plot, plot_tangents)
        self.body.plot_curvature(plot)

    def to_json(self):
        """Cheap way to store viol definition in a public, language independent, manner."""
        return jsonpickle.encode(self)

    @classmethod
    def from_json(cls, json_str):
        """Cheap way to restore viol definition in a public, language independent, manner."""
        return jsonpickle.decode(json_str)


def path_slice(path, T0=0.0, T1=1.0):
    """Return a new path snippet from T0 (start) to T1 (end)."""
    start, t0 = path.T2t(T0)
    end, t1 = path.T2t(T1)

    path_slice = Path(*path[start:end])
    path_slice[0]  = bpoints2bezier(split_bezier(path[start].bpoints(), t0)[1])
    path_slice[-1] = bpoints2bezier(split_bezier(path[end].bpoints(), t1)[0])

    return path_slice


def path_smooth(path):
    """Every adjoining segment starting handle and the previous segment ending handle is set to
    the average of the two handles."""
    for ix, seg in enumerate(path):
        if not isinstance(seg, CubicBezier):
            p0 = complex(seg.start)
            p1 = complex(seg.end)
            c1 = p0 + .30 * (p1 - p0) / seg.length()    # put control1 handle 30% of the way to end point
            c2 = p0 + .70 * (p1 - p0) / seg.length()    # put control2 handle 70% of the way to end point
            path[ix] = CubicBezier(p0, c1, c2, p1)      # simply a straight line with control points in line
            seg = path[ix]

        vec1 = path[ix - 1].end - path[ix - 1].control2
        vec2 = seg.control1 - seg.start
        new = vec1 + vec2 / 2.0
        path[ix].control1 = seg.start + new
        path[ix - 1].control2 = path[ix - 1].end - new
    return path


def path_compress(path, arc_thresh=5.0, turn_thresh=30):
    """Combine adjacent bezier curves if the curvature is low.  Don't combine more than arc_thresh arc length."""
    cpath = Path()
    ix = 0
    p0 = c1 = c2 = p1 = None
    arclen = 0.0
    while ix < len(path):
        # add a segment to combine
        if isinstance(path[ix], CubicBezier):
            if p0 is None:
                ix0 = ix
                p0 = complex(path[ix].start)
                c1 = complex(path[ix].control1)

            # XXX Should we increase magnitude of p0->c1? for each additional segment?

            # add on the segments arc length
            arclen += path[ix].length()

            # XXX Check here if the next segment is big turn, in which case terminate
            # calculate curvature relative to previous segment based on endpoint
            opp = path[ix - 1].end.real - path[ix - 1].start.real
            adj = path[ix - 1].end.imag - path[ix - 1].start.imag
            hyp = (opp ** 2 + adj ** 2) ** 0.5
            ang0 = np.rad2deg(np.arcsin(opp / hyp))
            opp = path[ix].end.real - path[ix].start.real
            adj = path[ix].end.imag - path[ix].start.imag
            hyp = (opp ** 2 + adj ** 2) ** 0.5
            ang1 = np.rad2deg(np.arcsin(opp / hyp))
            # determine if sufficent arc length has been achieved, or big curve coming, or end of path reached
            if (arclen > arc_thresh) or abs(ang0 - ang1) > turn_thresh or (ix == len(path) - 1):
                ix1 = ix
                p1 = complex(path[ix].end)
                c2 = complex(path[ix].control2)
        else:
            # we have something other than a CubicBezier (note that smoothing will elimate lines if done before this function!)
            if p0 is not None:
                # but we started CubicBezier segment to combine
                #     case 1: we have only one bezier segment
                #             so we just set ix1 = ix0 and trip to combine segment below
                #     case 2: we have a few previous bezier segments
                #             we can assume previous segment was final cubic (or
                #             the algorithm would have reset to no points)

                ix1 = max(ix0, ix - 1)
                if ix1 > ix0:
                    p1 = complex(path[ix1].end)
                    c2 = complex(path[ix1].control2)

        # combine segments
        if p1 is not None:
            if ix0 != ix1:
                # combine the segments
                cpath.append(CubicBezier(p0, c1, c2, p1))
                print ('combo found: ', len(path), len(cpath), ix, ix0, ix1, arclen)
            else:
                # no segments combined (could be too long, too twisted, end of path)
                # this case catches the situation of a short CubicBezier followed by a non CubicBezier (e.g. Line)
                cpath.append(path[ix])
            p0 = c1 = c2 = p1 = None
            arclen = 0.0

        # add segment to compressed path if not a cubic bezier
        if not isinstance(path[ix], CubicBezier):
            cpath.append(path[ix])
            # reset points to initial condition
            p0 = c1 = c2 = p1 = None

        # keep consuming further segments
        ix += 1
    return cpath


def path_flatten_top(path):
    """Flatten top tangent to horizontal."""
    path[0].control1 = complex(path[0].control1.real, path[0].start.imag)
    path[-1].control2 = complex(path[-1].control2.real, path[0].start.imag)
    return path


def path_flatten_bottom(path):
    """Flatten bottom tangent to horizontal."""
    # find the point closest to x=0 at bottom of curve which we assume to be in range T[.4, .6]
    f = lambda t: abs(path.point(t).real)
    T = minimize_scalar(f, bounds=(.4, .6), method='bounded', options={'xatol': 1e-9, 'disp': 0}).x
    # convert T to the segment and split the segment at t0 into two segments left and right of bottom point
    start, t0 = path.T2t(T)
    seg0, seg1 = [bpoints2bezier(b) for b in split_bezier(path[start].bpoints(), t0)]
    # remajigger the start, end, and control points to zero out the tangent
    seg0.end = complex(seg0.end.real, 0)
    seg0.control2 = complex(seg0.control2.real, 0)
    seg1.control1 = complex(seg1.control1.real, 0)
    seg1.start = complex(seg1.start.real, 0)
    # insert the new segment (left side of bottom), and overwrite the old segment with right side of bottom
    path.insert(start, seg0)
    path[start + 1] = seg1
    return path


def path_curvature(t1, path):
    delta = 0.02
    t0 = t1 - delta
    t2 = t1 + delta
    p0 = path.point(t0)
    p1 = path.point(t1)
    p2 = path.point(t2)
    pm = p0 + ((p2 - p0) / 2)
    w = np.linalg.norm(p2 - p0)
    h = np.linalg.norm(p1 - pm)
    r = (h / 2) + (w ** 2 / (8 * h))
    k = 1 / r

    return k


def path_find_slope(path, T0=0.0, T1=1.0, phi=None):
    """Find the point on a path between T0 and T1 where the slope matches phi."""
    if phi is None:
        phi = cmath.pi / 4.0

    # search the path for the precise point where slope is phi
    # XXX f = lambda t, slope:cmath.phase(path.unit_tangent(t))-slope
    # XXX return brentq(f, T0, T1, args=(phi))
    f = lambda t, slope: abs(cmath.phase(path.unit_tangent(t)) - slope)
    return minimize_scalar(f, bounds=(T0, T1), method='bounded', args=(phi), options={'xatol': 1e-5, 'disp': 0}).x


def path_find_curvature_min(path, T0=0.0, T1=1.0):
    """Find the point on a path between T0 and T1 where the curvature is smallest."""
    # search the path for smallest curvature
    return minimize_scalar(path_curvature, bounds=(T0, T1), args=(path), method='bounded', options={'xatol': 1e-5, 'disp': 0}).x


def path_compare(path, path_t0, path_t1, clothoid, clothoid_t0, clothoid_t1, nodes=100):
    tvec_path = np.linspace(path_t0, path_t1, nodes)
    tvec_clothoid = np.linspace(clothoid_t0, clothoid_t1, nodes)
    bez = np.array([path.point(t) for t in tvec_path])
    clo = np.array([clothoid.p(t) for t in tvec_clothoid])
    print(bez)
    print(clo)
    print(bez - clo)


def path_extrema_t(path, seg_list, ymin=0.0, ymax=1.0, reverse=False):
    """Based on svgpathtools function, but with bracketted search."""
    min_point = complex(0, 0)
    max_point = complex(0, 0)
    if not reverse:
        min_extreme = 0.0
        max_extreme = 0.0
    else:
        min_extreme = -1.0e99   # a small number
        max_extreme = 1.0e99    # a big number

    for ix in seg_list:
        seg = path[ix]
        # only consider segments in the selected range
        if seg.start.imag > ymin and seg.start.imag < ymax:
            t_min, t_max = bez_extrema_t(seg)
            p_min = seg.point(t_min)
            p_max = seg.point(t_max)
            if not reverse:
                if p_min.real < min_extreme:
                    min_point = path.t2T(ix, t_min)
                    min_extreme = p_min.real
                if p_max.real > max_extreme:
                    max_point = path.t2T(ix, t_max)
                    max_extreme = p_max.real
            else:
                # if we are left of centerline, we want to return p_max
                if seg.start.real < 0:
                    if p_max.real > min_extreme:
                        min_point = path.t2T(ix, t_max)
                        min_extreme = p_max.real
                # otherwise we want to return p_min
                else:
                    if p_min.real < max_extreme:
                        max_point = path.t2T(ix, t_min)
                        max_extreme = p_min.real
    return min_point, max_point


def path_closest_t(path, p):
    """Find the T of the point on the path closest to p."""
    f = lambda t: np.linalg.norm(path.point(t) - p)
    T = minimize_scalar(f, bounds=(0, 1.0), method='bounded', options={'xatol': 1e-5, 'disp': 0}).x
    return T


def bez_extrema_t(b):
    """Returns the minimum and maximum t values for the real axis (x) of a cubic bezier."""
    local_extremizers = [0, 1]
    if len(b) == 4:  # cubic case
        a = [b.real for b in b]
        denom = a[0] - 3 * a[1] + 3 * a[2] - a[3]
        if denom != 0:
            delta = a[1] ** 2 - (a[0] + a[1]) * a[2] + a[2]**2 + (a[0] - a[1]) * a[3]
            if delta >= 0:  # otherwise no local extrema
                sqdelta = math.sqrt(delta)
                tau = a[0] - 2 * a[1] + a[2]
                r1 = (tau + sqdelta) / denom
                r2 = (tau - sqdelta) / denom
                if 0 < r1 < 1:
                    local_extremizers.append(r1)
                if 0 < r2 < 1:
                    local_extremizers.append(r2)
            # initialize min/max point to first point
            b_min = bezier_point(a, 0)
            t_min = 0
            b_max = bezier_point(a, 0)
            t_max = 0
            for t in local_extremizers:
                b = bezier_point(a, t)
                if b > b_max:
                    b_max = b
                    t_max = t
                elif b < b_min:
                    b_min = b
                    t_min = t
            return t_min, t_max

    # find reverse standard coefficients of the derivative
    dcoeffs = bezier2polynomial(a, return_poly1d=True).deriv().coeffs

    # find real roots, r, such that 0 <= r <= 1
    local_extremizers += polyroots01(dcoeffs)
    # initialize min/max point to first point
    b_min = bezier_point(a, 0)
    t_min = 0
    b_max = bezier_point(a, 0)
    t_max = 0
    for t in local_extremizers:
        b = bezier_point(a, t)
        if b > b_max:
            b_max = b
            t_max = t
        elif b < b_min:
            b_min = b
            t_min = t
    return t_min, t_max


def phase_delta(p0, p1):
    phi = (cmath.phase(p0.tangent()) + 2 * cmath.pi) % (2 * cmath.pi)
    phi2 = (phi + cmath.pi) % (2 * cmath.pi)
    tan = (cmath.phase(p1.p() - p0.p()) + 2 * cmath.pi) % (2 * cmath.pi)

    if abs(phase_delta_min(phi2, tan)) < abs(phase_delta_min(phi, tan)):
        phi = phi2

    # determine if the clothoid should be clockwise or counterclockwise
    clockwise = (phase_delta_min(phi, tan) > 0)

    return phi, clockwise


def phase_delta_min(p1, p2):
    """Find the minimum angular distance between two angles. Result is [-pi, pi]."""
    return math.atan2(math.sin(p1 - p2), math.cos(p1 - p2))


@click.command()
@click.option('--filename', '-f', 'filename', default='clean.png', type=click.Path(),
              help='Path to a scanned viol image.')
def scan(filename):
    """Viol scan command.

    Scan a viola image, deduce the geometry, and curve fit the instrument with a
    combination of Bezier curves and Clothoids.
    """
    viola = Viola()
    viola.body_scan(filename)
    viola.plot()
    plt.show(block=False)
    input('<cr> to close program ->')
    plt.close()
