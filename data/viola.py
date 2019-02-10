#!/usr/bin/env python

import os
from collections import namedtuple
import tempfile
import json
import jsonpickle
import copy
import cmath
import numpy as np
from scipy.special import fresnel
from scipy.spatial import distance
from scipy.optimize import minimize_scalar, brentq
import matplotlib.pyplot as plt
import math
from math import ceil, log, sqrt

from io import BytesIO
from subprocess import Popen, PIPE, STDOUT
from PIL import Image, ImageFilter
from svgpathtools import Path, Line, CubicBezier, parse_path, svg2paths, svg2paths2
from svgpathtools import wsvg, disvg, bezier_point, bezier2polynomial, polynomial2bezier
from svgpathtools import bpoints2bezier, kinks, smoothed_path, split_bezier
from svgpathtools.polytools import polyroots01
from timeit import default_timer as timer
from time import sleep


class Clothoid(object):
    def __init__(self, scale=1, rotation=0, origin=(0,0), clockwise=True, T=2.1):
        self.T          = T
        self.scale      = scale
        self.rotation   = rotation
        self.origin     = origin
        self.clockwise  = clockwise

    def __repr__(self):
        fmt = '{}(scale={:.2f},rotation={:.2f},origin=({:.2f},{:.2f}),clockwise={:b})'
        return fmt.format(self.__class__.__name__, self.scale, self.rotation, self.origin[0], self.origin[1], self.clockwise)

    def sinVec(self):
        t = np.linspace(0, self.T, 1000)
        ss, cc = fresnel(t)
        twist = (1, -1)[bool(self.clockwise)]
        return (((self.scale * cc * math.cos(twist * self.rotation)) - \
                 (self.scale * ss * math.sin(twist * self.rotation))) + \
                self.origin[0])

    def cosVec(self):
        t = np.linspace(0, self.T, 1000)
        ss, cc = fresnel(t)
        twist = (1, -1)[bool(self.clockwise)]
        return (twist * ((self.scale * cc * math.sin(twist * self.rotation)) + \
                 (self.scale * ss * math.cos(twist * self.rotation))) + \
                self.origin[1])

    def p(self, t=0):
        return (complex(self.x(t), self.y(t)))

    def x(self, t=0):
        ss, cc = fresnel(t)
        twist = (1, -1)[bool(self.clockwise)]
        return (((self.scale * cc * math.cos(twist * self.rotation)) - \
                 (self.scale * ss * math.sin(twist * self.rotation))) + \
                self.origin[0])

    def y(self, t=0):
        ss, cc = fresnel(t)
        twist = (1, -1)[bool(self.clockwise)]
        return (twist * ((self.scale * cc * math.sin(twist * self.rotation)) + \
                 (self.scale * ss * math.cos(twist * self.rotation))) + \
                self.origin[1])
    
    def tangent(self, t=0):
        #XXX check that twist is implemented correctly
        cc = math.cos((cmath.pi/2)*t**2)
        ss = math.sin((cmath.pi/2)*t**2)
        twist = (1, -1)[bool(self.clockwise)]
        x = (((cc * math.cos(twist * self.rotation)) - \
              (ss * math.sin(twist * self.rotation))))
        y = twist * (((cc * math.sin(twist * self.rotation)) + \
              (ss * math.cos(twist * self.rotation))))
        return complex(x,y)

    def closest_t(self, p, max_t=2.2):
        """Return t on the clothoid closest to p."""
        f = lambda t:np.linalg.norm(self.p(t)-p)
        return minimize_scalar(f, bounds=(0, max_t), method='bounded', options={'xatol': 1e-5,'disp':0}).x

    def plot(self, plot, color='r-'):
        plot.plot(self.sinVec(), self.cosVec(), color, linewidth=1)

class Point(object):
    """A basic point."""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return ('{}(x={:.2f},y={:.2f})'.format(self.__class__.__name__, self.x, self.y))

    def plot(self, plot, color='b^'):
        plot.plot([self.x],[self.y],color)

class POI(object):
    """A point of interest."""
    def __init__(self, path, T=0, p=None):
        self.path = path
        if p is not None:
            self.closest_t(p)
        else:
            self.T = T

    def __repr__(self):
        return ('{}(T={:.2f},(x={:.2f},y={:.2f}))'.format(self.__class__.__name__, self.T, self.p().real, self.p().imag))

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
            tangent = self.path.unit_tangent(self.T-.01)
        return tangent

    def closest_t(self, p):
        """Set the POI to point on the path closest to p."""
        f = lambda t:np.linalg.norm(self.path.point(t)-p)
        self.T = minimize_scalar(f, bounds=(0, 1.0), method='bounded', options={'xatol': 1e-5,'disp':0}).x
        return self.T

    def plot(self, plot, color='b^'):
        plot.plot([self.x()],[self.y()],color)

class Tangent(object):
    """A unit tangent on a path at T"""
    def __init__(self, path, T=0, mag=50):
        try:
            tan = path.unit_tangent(T)
        except AssertionError:
            tan = path.unit_tangent(T+.001)
        self.start = path.point(T) - mag * tan
        self.end = path.point(T) + mag * tan

    def __repr__(self):
        return ('{}(start={},end={})'.format(self.__class__.__name__, self.start, self.end))

    def plot(self, plot, color='g-'):
        plot.plot([self.start.real,self.end.real],[self.start.imag,self.end.imag],color)

class Bout(object):
    """A bout from the POI left to the POI right"""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return ('{}(left={},right={})'.format(self.__class__.__name__, self.left, self.right))

    def plot(self, plot, color='r-'):
        plot.plot([self.left.x(),self.right.x()],[self.left.y(),self.left.y()],color)

class Corner(object):
    """A corner POI."""
    def __init__(self, poi):
        self.poi = poi

    def __repr__(self):
        return ('{}(poi={})'.format(self.__class__.__name__, self.poi))

    def plot(self, plot, color='b^'):
        self.poi.plot(plot, color)

class CL(object):
    """A centerline from the POI b(ottom) to the POI t(op)"""
    def __init__(self, bot, top_left, top_right):
        self.bot = bot
        self.top_left = top_left
        self.top_right = top_right

    def __repr__(self):
        return ('{}(bot={},top_left={}, top_right{})'.format(self.__class__.__name__, self.bot, self.top_left, self.top_right))

    def plot(self, plot, color='r-'):
        plot.plot([self.bot.x(),self.top_left.x()],[self.bot.y(),self.top_left.y()],color)


class Viola(object):
    """A generalized class of the geometry, features, and attributes of an instrument in the viol family."""
    def __init__(self):
        self.outline_clothoids = []
        self.outline_guesses = []
        self.outline_path = None
        self.outline_path_attributes = None
        self.outline_pathsvg_attributes = None
        self.outline_feature_bbox = []
        self.outline_feature_bout_upper = None
        self.outline_feature_bout_middle = None
        self.outline_feature_bout_lower = None
        self.outline_feature_centerline = None
        self.outline_feature_corner_upper_left = None
        self.outline_feature_corner_lower_left = None
        self.outline_feature_corner_upper_right = None
        self.outline_feature_corner_lower_right = None
        self.outline_feature_turn_upper_left = None
        self.outline_feature_turn_lower_left = None
        self.outline_feature_turn_lower_right = None
        self.outline_feature_turn_upper_right = None
        self.outline_feature_turn_ul_tangent = None
        self.outline_feature_turn_ll_tangent = None
        self.outline_feature_turn_lr_tangent = None
        self.outline_feature_turn_ur_tangent = None
        self.outline_feature_45_upper_left = None
        self.outline_feature_45_lower_left = None
        self.outline_feature_45_lower_right = None
        self.outline_feature_45_upper_right = None
        self.outline_feature_45_upper_left_tangent = None
        self.outline_feature_45_lower_left_tangent = None
        self.outline_feature_45_lower_right_tangent = None
        self.outline_feature_45_upper_right_tangent = None

    def scan(self, imageFile, dpi=300, threshold=205, despeckle=10):
        img = Image.open(imageFile)
        img = img.convert(mode="L")

        # convert from input dots per inch to 100 dots per cm (.1mm resolution)
        resize = 2540.0/(10.0 * dpi)
        w, h = img.size
        img = img.resize((int(w * resize), int(h * resize)), Image.LANCZOS)
        img = img.point(lambda x: 0 if x < threshold else 255, '1')

        #XXX one could preview the threshold result with img.show()

        # convert the image to a bitmap memory file for input to potrace
        bmp = BytesIO()
        img.save(bmp, format='BMP')
        bmp.seek(0)

        # execute potrace as a subprocess filter stdin to stdout
        p = Popen(['potrace','-s', '-t', str(despeckle)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        svg_tmp = tempfile.NamedTemporaryFile()
        svg_tmp.write(p.communicate(input=bmp.read())[0].decode())
        svg_tmp.flush()

        # parse the svg file to extract the cubic bezier curve paths
        paths, attributes, svg_attributes = svg2paths2(svg_tmp.name)
        svg_tmp.close()

        #XXX assume here that the longest path is the outline we want, and rest is clutter
        # we could try different threshold values until a reasonble path count is found.
        # we could also detect split long paths and join them together
        path = paths[0]
        for p in paths:
            if p.length() > path.length():
                path = p

        # outline path traces both outside and inside the trace... we only want inside trace
        # XXX we assume here that potrace closes the outside curve before starting the
        # inside curve.  It is probably more defensive to chose the first segment endpoint (after t > 0.1)
        # that has the closest Euclidean distance to the starting point.
        # an assumption that potrace starts the path at top most part of viola has probably
        # snuck into the code somewhere, so it would be good check and correct those conditions.

        endpoints = [ix for ix, seg in enumerate(path) if seg.point(1) == path.point(0)]
        del(path[endpoints[0]+1:])
        
        # check that the viola outline path is closed
        assert(path.iscontinuous())

        # normalize the path for (0,0) at the centerline of the bottom of the instrument
        # XXX A proper centerline would be to consider vertical extremi, or average(x) for all x,
        # or svgpathtools.path.point(0.5). It also may be tilted, so a rotation is required.

        xmin, xmax, ymin, ymax = path.bbox()                    # use a bounding box to determine x,y extremi
        #XXX xshift = ((xmax - xmin)/2.0) + xmin                # calculate shift to center y axis on centerline
        xshift = path.point(0.0).real                           # T=0 appears to find top most point
        scale = 1000.0 / 10.0**(ceil(np.log10(ymax - ymin)))    # calculate scaling factor for pixel == 0.1mm
        path = path.translated(complex(-xshift, -ymin))         # complex translation vector
        path = path.scaled(scale)                               # scale path to 10 pixels/mm (curves get detached)
        for ix, seg in enumerate(path[:-1]):
            seg.end = path[ix+1].start                          # reattach curves so path.iscontinuous()
        path[-1].end = path[0].start


        self.outline_path = path
        self.outline_path_attributes = attributes
        self.outline_pathsvg_attributes = svg_attributes        # XXX Seems not to like svg version of 1.0
        self.outline_feature_bbox = path.bbox()

    def path_smooth(self, path=None):
        """Every adjoining segment starting handle and the previous segment ending handle is set to
        the average of the two handles."""
        if path is None:
            path = self.outline_path

        for ix,seg in enumerate(path):
            if not isinstance(seg, CubicBezier):
                p0 = complex(seg.start)
                p1 = complex(seg.end)
                c1 = p0 + .30 * (p1 - p0)/seg.length()      # put control1 handle 30% of the way to end point
                c2 = p0 + .70 * (p1 - p0)/seg.length()      # put control2 handle 70% of the way to end point
                path[ix] = CubicBezier(p0, c1, c2, p1)      # simply a straight line with control points in line
                seg = path[ix]
                
            vec1 = path[ix-1].end - path[ix-1].control2
            vec2 = seg.control1 - seg.start
            new = vec1+vec2/2.0
            path[ix].control1 = seg.start + new
            path[ix-1].control2 = path[ix-1].end - new
        return path

    def outline_path_compress(self, path=None, arc_thresh=5.0, turn_thresh=30):
        """Combine adjacent bezier curves if the curvature is low.  Don't combine more than arc_thresh arc length."""
        if path is None:
            path = self.outline_path

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
                opp = path[ix-1].end.real - path[ix-1].start.real
                adj = path[ix-1].end.imag - path[ix-1].start.imag
                hyp = (opp**2 + adj**2)**0.5
                ang0 = np.rad2deg(np.arcsin(opp/hyp))
                opp = path[ix].end.real - path[ix].start.real
                adj = path[ix].end.imag - path[ix].start.imag
                hyp = (opp**2 + adj**2)**0.5
                ang1 = np.rad2deg(np.arcsin(opp/hyp))
                # determine if sufficent arc length has been achieved, or big curve coming, or end of path reached
                if (arclen > arc_thresh) or abs(ang0-ang1) > turn_thresh or (ix == len(path) - 1):
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
                    cpath.append(CubicBezier(p0,c1,c2,p1))
                else:
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
        
    def outline_path_features(self, bout_tol=0.1, corner_curve_tol=1.0):
        """Use properties of a Viola to establish bout locations and widths, corner locations, etc."""
        path = self.outline_path

        # flatten upper tangent
        top_left = POI(path, T=0.0)
        top_right = POI(path, T=1.0)
        path[0].control1 = complex(path[0].control1.real,path[0].start.imag)
        path[-1].control2 = complex(path[-1].control2.real,path[0].start.imag)

        # flatten bottom tangent
        bot = POI(path, p=complex(top_left.x(),0))
        start,t0 = path.T2t(bot.T)
        print start,t0
        seg0 = bpoints2bezier(split_bezier(path[start].bpoints(),t0)[0])
        seg1 = bpoints2bezier(split_bezier(path[start].bpoints(),t0)[1])
        seg0.end = complex(seg0.end.real,0)
        seg0.control2 = complex(seg0.control2.real,0)
        seg1.control1 = complex(seg1.control1.real,0)
        seg1.start = complex(seg1.start.real,0)
        path.insert(start,seg0)
        path[start+1] = seg1

        # now we establish the viol centerline
        bot = POI(path, p=complex(top_left.x(),0))

        self.outline_feature_centerline = CL(bot, top_left, top_right)
        print math.degrees(cmath.phase(bot.tangent()))

        # we need a vectorized function to find the tangent of a curve
        vec_f_tan = np.vectorize(lambda t:seg.unit_tangent(t))

        bouts = []
        corners = []
        seg = self.outline_path[0]
        seg_prev_tan = np.average(vec_f_tan(np.linspace(0.0,1.0,10)))

        # We sweep around all segements of the viol outline and nominate all possible bout features
        # to bouts[] based on a vertical unit tangent and corner features to corners[] based on
        # significant changes in direction.
        for ix, seg in enumerate(self.outline_path):
            # Points of interest:
            #   1. Vertical lines (bouts) have curvature (0+-1j)
            #   2. Horizontal lines (top & bottom) have curvature (+-1+0j)
            #   3. Corners have segment to segment jump of curvature > .5

            seg_tan = np.average(vec_f_tan(np.linspace(0.0,1.0,10)))
            d_real = max(seg_tan.real,seg_prev_tan.real) - min(seg_tan.real,seg_prev_tan.real)
            d_imag = max(seg_tan.imag,seg_prev_tan.imag) - min(seg_tan.imag,seg_prev_tan.imag)
            if (abs(seg_tan.real) < bout_tol) and (abs(seg_tan.imag) > (1.0 - bout_tol)):
                bouts.append(ix)
            if (abs(d_real) + abs(d_imag) > corner_curve_tol):
                corners.append(ix)
            seg_prev_tan = seg_tan

        # Now we bracket our search to determine the real bouts

        #XXX there is an assumption of bouts laying within the viol terciles
        top = self.outline_feature_centerline.top_left.y()
        # Find the upper left and right bout points in upper third of scan
        start, end=self.extrema_in_range(bouts,top*2.0/3.0,top)
        self.outline_feature_bout_upper = Bout(POI(path,start),POI(path,end))

        # Find the lower left and right bout points
        start, end=self.extrema_in_range(bouts,0.0,top*1.0/3.0)
        self.outline_feature_bout_lower = Bout(POI(path,start),POI(path,end))

        # Find the middle left and right bout points
        start, end=self.extrema_in_range(bouts,top*1.0/3.0,top*2.0/3.0, reverse=True)
        self.outline_feature_bout_middle = Bout(POI(path,start),POI(path,end))

        # Now we bracket our search based on bout locales to determine the real corners

        # Find the lower corners
        #XXX There could be residual segments above lower bout that are left/right of corner!
        bot = self.outline_feature_bout_lower.left.y()
        top = self.outline_feature_bout_middle.left.y()
        start, end=self.extrema_in_range(corners,bot,top)
        self.outline_feature_corner_lower_left = POI(path,start)
        self.outline_feature_corner_lower_right = POI(path,end)
        #self.outline_feature_corner_lower_left_tangent = Tangent(path,start+.003)
        #self.outline_feature_corner_lower_left_tangent_poi = POI(path,start+.003)
        #self.outline_feature_corner_lower_left_tangent2 = Tangent(path,start-.003)
        #self.outline_feature_corner_lower_left_tangent2_poi = POI(path,start-.003)
        #self.outline_feature_corner_lower_right_tangent = Tangent(path,end-.003)
        #self.outline_feature_corner_lower_right_tangent_poi = POI(path,end-.003)
        #self.outline_feature_corner_lower_right_tangent2 = Tangent(path,end+.003)
        #self.outline_feature_corner_lower_right_tangent2_poi = POI(path,end+.003)

        # Find the upper corners
        #XXX There could be residual segments below upper bout that are left/right of corner!
        bot = self.outline_feature_bout_middle.left.y()
        top = self.outline_feature_bout_upper.left.y()
        start, end=self.extrema_in_range(corners,bot,top)
        self.outline_feature_corner_upper_left = POI(path,start)
        self.outline_feature_corner_upper_right = POI(path,end)
        #self.outline_feature_corner_upper_left_tangent = Tangent(path,start+.003)
        #self.outline_feature_corner_upper_left_tangent_poi = POI(path,start+.003)
        #self.outline_feature_corner_upper_left_tangent2 = Tangent(path,start-.003)
        #self.outline_feature_corner_upper_left_tangent2_poi = POI(path,start-.003)
        #self.outline_feature_corner_upper_right_tangent = Tangent(path,end-.003)
        #self.outline_feature_corner_upper_right_tangent_poi = POI(path,end-.003)
        #self.outline_feature_corner_upper_right_tangent2 = Tangent(path,end+.003)
        #self.outline_feature_corner_upper_right_tangent2_poi = POI(path,end+.003)

        # Now we bracket our search based on bouts and corners to find the turns (change of direction)

        f = lambda t:abs(path.unit_tangent(t).imag/path.unit_tangent(t).real)   # steepest tangent from real axis

        T0 = self.outline_feature_bout_upper.left.T
        T1 = self.outline_feature_corner_upper_left.T
        T = minimize_scalar(f, bounds=(T0, T1), method='bounded', options={'xatol': 1e-5,'disp':0}).x
        self.outline_feature_turn_upper_left = POI(path,T)
        self.outline_feature_turn_ul_tangent = Tangent(path,T)

        T0 = self.outline_feature_corner_lower_left.T
        T1 = self.outline_feature_bout_lower.left.T
        T = minimize_scalar(f, bounds=(T0, T1), method='bounded', options={'xatol': 1e-5,'disp':0}).x
        self.outline_feature_turn_lower_left = POI(path,T)
        self.outline_feature_turn_ll_tangent = Tangent(path,T)

        T0 = self.outline_feature_bout_lower.right.T
        T1 = self.outline_feature_corner_lower_right.T
        T = minimize_scalar(f, bounds=(T0, T1), method='bounded', options={'xatol': 1e-5,'disp':0}).x
        self.outline_feature_turn_lower_right = POI(path,T)
        self.outline_feature_turn_lr_tangent = Tangent(path,T)

        T0 = self.outline_feature_corner_upper_right.T
        T1 = self.outline_feature_bout_upper.right.T
        T = minimize_scalar(f, bounds=(T0, T1), method='bounded', options={'xatol': 1e-5,'disp':0}).x
        self.outline_feature_turn_upper_right = POI(path,T)
        self.outline_feature_turn_ur_tangent = Tangent(path,T)

        # Now we search for the 45 degree slopes on upper and lower corners (where the clothoids join)

        T0=0.015
        T1=self.outline_feature_bout_upper.left.T - 0.015
        T = path_find_slope(path, T0, T1, phi=-3.0*cmath.pi/4.0)
        self.outline_feature_45_upper_left = POI(path,T)
        self.outline_feature_45_upper_left_tangent = Tangent(path,T)

        T0 = self.outline_feature_bout_lower.left.T + 0.015
        T1 = self.outline_feature_centerline.bot.T - 0.015
        T = path_find_slope(path, T0, T1, phi=-cmath.pi/4.0)
        self.outline_feature_45_lower_left = POI(path,T)
        self.outline_feature_45_lower_left_tangent = Tangent(path,T)

        T0 = self.outline_feature_centerline.bot.T + 0.015
        T1 = self.outline_feature_bout_lower.right.T -0.015
        T = path_find_slope(path, T0, T1, phi=cmath.pi/4.0)
        self.outline_feature_45_lower_right = POI(path,T)
        self.outline_feature_45_lower_right_tangent = Tangent(path,T)

        T0 = self.outline_feature_bout_upper.right.T + 0.015
        T1 = self.outline_feature_centerline.top_right.T - 0.015
        T = path_find_slope(path, T0, T1, phi=3*cmath.pi/4.0)
        self.outline_feature_45_upper_right = POI(path,T)
        self.outline_feature_45_upper_right_tangent = Tangent(path,T)

    def outline_clothoids_find(self):
        """Define a set of clothoids based on path features."""
        #XXX I can't think of an obvious way to make this less ugly! A global dictionary?!
        clist = [
            [self.outline_feature_centerline.top_left, self.outline_feature_45_upper_left],
            [self.outline_feature_turn_upper_left, self.outline_feature_45_upper_left],
            [self.outline_feature_turn_upper_left, self.outline_feature_corner_upper_left],
            [self.outline_feature_bout_middle.left, self.outline_feature_corner_upper_left],
            [self.outline_feature_bout_middle.left, self.outline_feature_corner_lower_left],
            [self.outline_feature_turn_lower_left, self.outline_feature_corner_lower_left],
            [self.outline_feature_turn_lower_left, self.outline_feature_45_lower_left],
            [self.outline_feature_centerline.bot, self.outline_feature_45_lower_left],
            [self.outline_feature_centerline.bot, self.outline_feature_45_lower_right],
            [self.outline_feature_turn_lower_right, self.outline_feature_45_lower_right],
            [self.outline_feature_turn_lower_right, self.outline_feature_corner_lower_right],
            [self.outline_feature_bout_middle.right, self.outline_feature_corner_lower_right],
            [self.outline_feature_bout_middle.right, self.outline_feature_corner_upper_right],
            [self.outline_feature_turn_upper_right, self.outline_feature_corner_upper_right],
            [self.outline_feature_turn_upper_right, self.outline_feature_45_upper_right],
            [self.outline_feature_centerline.top_right, self.outline_feature_45_upper_right]
        ]

        # iterate over every clothoid to construct
        for ix,points in enumerate(clist):
            p0,p1 = [points[0],points[1]] 

            is_corner = p1 in [self.outline_feature_corner_upper_left, self.outline_feature_corner_upper_right,
                               self.outline_feature_corner_lower_left, self.outline_feature_corner_lower_right]

            # calculate transform based on entry angle and cw/ccw twist
            rotation, clockwise  = twist_calc(p0,p1)
            # estimate the scale based on arclength of bezier path
            if p1.T > p0.T:
                arclen = self.outline_path.length(p0.T, p1.T)
                if is_corner:
                    tan = (cmath.phase(p1.path.unit_tangent(p1.T - .003)) + (2 * cmath.pi)) % (2 * cmath.pi)
                else:
                    tan = (cmath.phase(p1.path.unit_tangent(p1.T)) + (2 * cmath.pi)) % (2 * cmath.pi)
                tan2 = (tan + cmath.pi) % (2 * cmath.pi)
            else:
                arclen = self.outline_path.length(p1.T, p0.T)
                if p0.T > .997:
                    tan = (cmath.phase(-p1.path.unit_tangent(p1.T)) + (2 * cmath.pi)) % (2 * cmath.pi)
                else:
                    tan = (cmath.phase(-p1.path.unit_tangent(p1.T + .003)) + (2 * cmath.pi)) % (2 * cmath.pi)
                tan2 = (tan + cmath.pi) % (2 * cmath.pi)

            #phi = min(tan, tan2)
            phi = abs(phase_delta_min(rotation, tan))
            #print "Anus", math.degrees(tan), math.degrees(phi), math.degrees(phi1), math.degrees(phi2)

            if phi < cmath.pi/8:
                phi = max(tan, tan2)
                print "Fuck", math.degrees(tan), math.degrees(tan2), math.degrees(phi)

            t = math.sqrt((2 * phi)/cmath.pi)
            scale = arclen/t

            fmt = "Cl{:2d}: t0:{:.2f} t1:{:.2f} rot:{:6.2f} phi:{:6.2f} arc:{:6.2f} scale:{:5.2f} eul_t:{:.2f}"
            print fmt.format(ix+1, p0.T, p1.T, math.degrees(rotation), math.degrees(phi), arclen, scale, t)

            cl = Clothoid(scale, rotation, (p0.x(),p0.y()), clockwise)
            self.outline_clothoids.append(cl)

            #XXX we want minimize error with a minimize search for scale

            #XXX convert the next block to brentq search for rotation_error == 0
            #for i in range(0,10):
                #cl = Clothoid(scale, rotation, (p0.x(),p0.y()), clockwise)
                #t = cl.closest_t(p1)
                #ph1 = cmath.phase(p1 - p0)
                #ph2 = cmath.phase(cl.p(t) - p0)

                #print "p1:", p1
                #print "t, p(t):", t, cl.p(t)
                #print "ph1, ph2, delta, min_delta_degrees:", ph1, ph2, ph1 - ph2, phase_delta_min(ph1, ph2)
                #print "rotation", rotation, math.degrees(rotation)
                #self.outline_guesses.append(Point(cl.x(t),cl.y(t)))
                #self.outline_clothoids.append(cl)
                #rotation = rotation + (ph1 - ph2)

        #path_compare(self.outline_path, 0.0, self.outline_feature_45_upper_left.T, cl, 0.0, t, nodes=10)

        #XXX Here is where we iterate on scale to find best scale

        #self.outline_clothoids.append(cl)
        

    def plot (self, plot=None):
        """Plot a viola using matplotlib.  Note this does not display the plot."""
        #XXX This function needs color arguments
        #XXX This function needs plot size and axis arguments
        #XXX This function needs an "exclude" features list
        #XXX This function needs an "include" features list
        if plot is None:
            plt.figure(figsize=(6,8.4))
            plt.axis([-150,150,0,420])
            plot = plt
        # Use a self referential string search to establish plottable features.
        features = [(key) for key, value in self.__dict__.iteritems() if key.startswith("outline_feature")]
        for feature in features:
            try:
                getattr(self, feature).plot(plot)
            except AttributeError:
                pass

        # Plot the clothoids (if any)
        for clothoid in self.outline_clothoids:
            clothoid.plot(plot)

        # Plot the guesses

        for guess in self.outline_guesses:
            guess.plot(plot)

        # Plot outline path by digitizing the bezier curve(s) with 5000 points
        x,y = zip(*[(self.outline_path.point(T).real,self.outline_path.point(T).imag) for T in np.linspace(0.0,1.0,5000)])
        plot.plot(x,y,'b-')
        return plot

    def extrema_in_range(self,seg_list,ymin,ymax,reverse=False):
        """Based on svgpathtools function, but with bracketted search."""
        #XXX This is just a utility function.  It should not be a class method
        min_point = complex(0,0)
        max_point = complex(0,0)
        if not reverse:
            min_extreme = 0.0
            max_extreme = 0.0
        else:
            min_extreme = -1.0e99   # a small number
            max_extreme = 1.0e99    # a big number

        for ix in seg_list:
            seg = self.outline_path[ix]
            # only consider segments in the selected range
            if seg.start.imag > ymin and seg.start.imag < ymax:
                t_min, t_max = bez_extrema_t(seg)
                p_min = seg.point(t_min)
                p_max = seg.point(t_max)
                if not reverse:
                    if p_min.real < min_extreme:
                        min_point = self.outline_path.t2T(ix,t_min)
                        min_extreme = p_min.real
                    if p_max.real > max_extreme:
                        max_point = self.outline_path.t2T(ix,t_max)
                        max_extreme = p_max.real
                else:
                    # if we are left of centerline, we want to return p_max
                    if seg.start.real < 0:
                        if p_max.real > min_extreme:
                            min_point = self.outline_path.t2T(ix,t_max)
                            min_extreme = p_max.real
                    else:
                    # otherwise we want to return p_min
                        if p_min.real < max_extreme:
                            max_point = self.outline_path.t2T(ix,t_min)
                            max_extreme = p_min.real
        return min_point, max_point

    def to_json(self):
        """Cheap way to store viol definition in a public, language independent, manner."""
        return jsonpickle.encode(self)

    @classmethod
    def from_json(cls,json_str):
        """Cheap way to restore viol definition in a public, language independent, manner."""
        return jsonpickle.decode(json_str)

def path_slice(path, T0=0.0, T1=1.0):
    """Return a new path snippet from T0 (start) to T1 (end)."""
    start,t0 = path.T2t(T0)
    end,t1 = path.T2t(T1)

    path_slice = Path(*path[start:end])
    path_slice[0]  = bpoints2bezier(split_bezier(path[start].bpoints(),t0)[1])
    path_slice[-1] = bpoints2bezier(split_bezier(path[end].bpoints(),t1)[0])

    return path_slice
    
def path_find_slope(path, T0=0.0, T1=1.0, phi=None):
    """Find the segment where the slope exists within it based on segment end points
    this avoids being tricked by a local minima in another segment."""
    if phi is None:
        phi = cmath.pi/4.0

    # search the path for the precise point where slope is phi
    f = lambda t,slope:cmath.phase(path.unit_tangent(t))-slope
    return brentq(f, T0, T1, args=(phi))

def phase_delta_min(p1, p2):
    """Find the minimum angular distance between two angles. Result is [-pi,pi]."""
    return math.atan2(math.sin(p1-p2), math.cos(p1-p2))

def twist_calc(p0, p1):
    phi = (cmath.phase(p0.tangent()) + 2 * cmath.pi) % (2 * cmath.pi)
    phi2 = (phi + cmath.pi) % (2 * cmath.pi)
    tan = (cmath.phase(p1.p() - p0.p()) + 2 * cmath.pi) % (2 * cmath.pi)

    if abs(phase_delta_min(phi2, tan)) < abs(phase_delta_min(phi, tan)):
        phi = phi2

    # determine if the clothoid should be clockwise or counterclockwise
    clockwise = (phase_delta_min(phi, tan) > 0)

    return phi, clockwise

def bez_extrema_t(b):
    """Returns the minimum and maximum t values for the real axis (x) of a cubic bezier."""
    local_extremizers = [0, 1]
    if len(b) == 4:  # cubic case
        a = [b.real for b in b]
        denom = a[0] - 3*a[1] + 3*a[2] - a[3]
        if denom != 0:
            delta = a[1]**2 - (a[0] + a[1])*a[2] + a[2]**2 + (a[0] - a[1])*a[3]
            if delta >= 0:  # otherwise no local extrema
                sqdelta = sqrt(delta)
                tau = a[0] - 2*a[1] + a[2]
                r1 = (tau + sqdelta)/denom
                r2 = (tau - sqdelta)/denom
                if 0 < r1 < 1:
                    local_extremizers.append(r1)
                if 0 < r2 < 1:
                    local_extremizers.append(r2)
            # initialize min/max point to first point
            b_min = bezier_point(a,0)
            t_min = 0
            b_max = bezier_point(a,0)
            t_max = 0
            for t in local_extremizers:
                b = bezier_point(a,t)
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
    b_min = bezier_point(a,0)
    t_min = 0
    b_max = bezier_point(a,0)
    t_max = 0
    for t in local_extremizers:
        b = bezier_point(a,t)
        if b > b_max:
            b_max = b
            t_max = t
        elif b < b_min:
            b_min = b
            t_min = t
    return t_min, t_max

def path_compare(path, path_t0, path_t1, clothoid, clothoid_t0, clothoid_t1, nodes=100):
    tvec_path = np.linspace(path_t0,path_t1,nodes)
    tvec_clothoid = np.linspace(clothoid_t0,clothoid_t1,nodes)
    bez = np.array([path.point(t) for t in tvec_path])
    clo = np.array([clothoid.p(t) for t in tvec_clothoid])
    print bez
    print clo
    print bez - clo

# Main entry point
#

viola = Viola()
viola.scan("clean.png")
viola.outline_path = viola.path_smooth()
viola.outline_path = viola.outline_path_compress()
viola.outline_path_features()
viola.outline_clothoids_find()

plt = viola.plot()
plt.show(block=False)
raw_input('<cr> to close program ->')
plt.close()
