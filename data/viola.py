#!/usr/bin/env python

import os
import tempfile
import json
import jsonpickle
import numpy as np
from scipy.special import fresnel
from scipy.spatial import distance
import matplotlib.pyplot as plt
import math
from math import ceil, log, sqrt

from io import BytesIO
from subprocess import Popen, PIPE, STDOUT
from PIL import Image, ImageFilter
from svgpathtools import Path, Line, CubicBezier, parse_path, svg2paths, svg2paths2, wsvg, disvg, bezier_point, bezier2polynomial
from timeit import default_timer as timer


t = np.linspace(0,2.1, 1000)
ss, cc = fresnel(t)

class Clothoid(object):
    def __init__(self, scale=1, rotation=0, origin=(0,0), hflip=1, vflip=1):
        self.scale      = scale
        self.rotation   = rotation
        self.origin     = origin
        self.hflip      = hflip
        self.vflip      = vflip

    def sinVec(self):
        return (self.hflip * \
                ((self.scale * cc * math.cos(self.rotation)) - \
                 (self.scale * ss * math.sin(self.rotation))) + \
                self.origin[0])

    def cosVec(self):
        return (self.vflip * \
                ((self.scale * cc * math.sin(self.rotation)) + \
                 (self.scale * ss * math.cos(self.rotation))) + \
                self.origin[1])
    
class Viola(object):
    def __init__(self):
        self.clothoids = None
        self.scan_path = None
        self.scan_attributes = None
        self.scan_svg_attributes = None

    def scan(self, imageFile, dpi=300, threshold=205, despeckle=10):
        img = Image.open(imageFile)
        img = img.convert(mode="L")

        # convert from input dots per inch to 100 dots per cm (.1mm resolution)
        resize = 2540.0/(10.0 * dpi)
        w, h = img.size
        img = img.resize((int(w * resize), int(h * resize)), Image.LANCZOS)
        img = img.point(lambda x: 0 if x < threshold else 255, '1')

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

        # assume here that the longest path is the outline we want, and rest is clutter
        path = paths[0]
        for p in paths:
            if p.length() > path.length():
                path = p

        # outline path traces both outside and inside the trace... we only want inside trace
        # XXX we assume here that potrace closes the outside curve before starting the
        # inside curve.  It is probably more defensive to chose the first segment endpoint (after t > 0.1)
        # that has the closest Euclidean distance to the starting point.

        endpoints = [ix for ix, seg in enumerate(path) if seg.point(1) == path.point(0)]
        del(path[endpoints[0]+1:])
        
        # normalize the path for (0,0) at the centerline of the bottom of the instrument

        xmin, xmax, ymin, ymax = path.bbox()                    # use a bounding box to determine x,y extremis
        xshift = ((xmax - xmin)/2.0) + xmin                     # calculate shift to center y axis on centerline
        scale = 1000.0 / 10.0**(ceil(np.log10(ymax - ymin)))    # calculate scaling factor for pixel == 0.1mm
        path = path.translated(complex(-xshift, -ymin))         # complex translation vector
        path = path.scaled(scale)                               # scale path to 10 pixels/mm

        self.scan_path = path
        self.scan_attributes = attributes
        self.scan_svg_attributes = svg_attributes   # XXX Seems not to like svg version of 1.0
        
    def metrics_from_scan(self):
        """Use properties of a Viola to establish bout location and widths, corner locations, etc."""
        #disvg([path], 'g')
        #quit()
        #del(viola.scan_path[:550])
        #del(viola.scan_path[3:])

        prev = "X"
        extrema = []
        for ix, seg in enumerate(self.scan_path):
            # do we have a segment of interest based upon:
            #    1. A change of tangent sign in the x-axis? (vertical tangent!)

            # start by looking at the two end points
            #dx = self.scan_path[0].end.real - self.scan_path[0].start.real
            #dy = self.scan_path[0].end.imag - self.scan_path[0].start.imag

            pt = seg.unit_tangent(0.5)
            pprev = prev
            if isinstance(seg, CubicBezier):
                if (pt.real >= 0) and (pt.imag > 0) and prev != "1":
                    prev = "1"
                if (pt.real < 0) and (pt.imag >= 0) and prev != "2":
                    prev = "2"
                if (pt.real < 0) and (pt.imag < 0) and prev != "3":
                    prev = "3"
                if (pt.real >= 0) and (pt.imag < 0) and prev != "4":
                    prev = "4"

                #if prev != pprev:
                if True:
                    #print seg
                    #print [p.real for p in seg]
                    t_min, t_max = bez_extrema_t([p.real for p in seg])
                    p_min = seg.point(t_min)
                    p_max = seg.point(t_max)
                    if p_min.real <= 0:
                        extreme = p_min
                        extreme_t = t_min
                    else:
                        extreme = p_max
                        extreme_t = t_max

                    extrema.append((ix, extreme_t, extreme.real, extreme.imag))
                    
                #print ix, tuple(np.subtract((extreme.real, extreme.imag),(xshift,ymin))), seg.unit_tangent(extreme_t), seg.curvature(extreme_t)
        extrema = sorted (extrema, reverse=True, key=lambda extreme: viola.scan_path[extreme[0]].curvature(extreme[1]))
        extrema_x = []
        extrema_y = []
        for extreme in extrema:
            extrema_x.append(extreme[2])
            extrema_y.append(extreme[3])
        return extrema_x, extrema_y
        #print extrema

        #quit()

        #XXX start work here on feature extraction (vertical tangents, horizontal tangents, corners)
        #for T in np.linspace(.321,.323,10):
            #k,t = viola.scan_path.T2t(T)
            #print k, T, t, (scale * (viola.scan_path[k].point(t).real - xshift), scale * (viola.scan_path[k].point(t).imag - ymin))
            #print "Tangent: ", viola.scan_path[k].unit_tangent(t)

        #k,t = viola.scan_path.T2t(.321)
        return

    def plot (self, plot):
        for clothoid in self.clothoids:
            plot.plot(clothoid.sinVec(), clothoid.cosVec(), 'r-', linewidth=1)
        #XXX Need to calculate outline points from Bezier curves
        #plt.plot(*zip(*self.outline))

    # XXX add reflection
    # def reflect(self):
        #if reflect:
        #    for cl in clothoids:
        #        cl.append(  cant append to current iteraration  need to build list

    def to_json(self):
        return jsonpickle.encode(self)

    @classmethod
    def from_json(cls,json_str):
        return jsonpickle.decode(json_str)

class Curve(object):
    def __init__(self, vector, min_x, max_x, min_y, max_y):
        self.curve = []
        clip_start = False
        for (x,y) in vector:
            if x < min_x or x > max_x or y < min_y or y > max_y:
                if clip_start:
                    break
                else:
                    clip_start = True
            else:
                self.curve.append((x,y))
    
def bez_extrema_t(p):
    """returns the minimum and maximum for any real cubic bezier"""
    local_extremizers = [0, 1]
    if len(p) == 4:  # cubic case
        a = [p.real for p in p]
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

    #XXX bail out on tricky curves until fix of polyroots01 complete
    return 0.0, 1.0
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

def scan_to_nodes(path):
    x = []
    y = []
    for t in np.linspace(0.0,1.0,1000):
        x.append(path.point(t).real)
        y.append(path.point(t).imag)
    return x,y

# Main entry point
#

with open("salo.json", 'rb') as f:
    viola = Viola.from_json(f.read())

viola.scan("clean.png")

x,y = scan_to_nodes(viola.scan_path)

plt.figure(figsize=(6,8.4))
plt.axis([-150,150,0,420])
plt.plot(x,y,'r-')

x,y = viola.metrics_from_scan()
plt.plot (x,y, 'bo', ms=2.0)

viola.plot(plt)

plt.show(block=False)

raw_input('<cr> to close program ->')

plt.close()

