#!/usr/bin/env python

import os
import tempfile
import json
import jsonpickle
import copy
import numpy as np
from scipy.special import fresnel
from scipy.spatial import distance
import matplotlib.pyplot as plt
import math
from math import ceil, log, sqrt

from io import BytesIO
from subprocess import Popen, PIPE, STDOUT
from PIL import Image, ImageFilter
from svgpathtools import Path, Line, CubicBezier, parse_path, svg2paths, svg2paths2
from svgpathtools import wsvg, disvg, bezier_point, bezier2polynomial, kinks, smoothed_path
from timeit import default_timer as timer
from time import sleep


class Clothoid(object):
    def __init__(self, scale=1, rotation=0, origin=(0,0), hflip=1, vflip=1):
        self.scale      = scale
        self.rotation   = rotation
        self.origin     = origin
        self.hflip      = hflip
        self.vflip      = vflip


    def sinVec(self):
        t = np.linspace(0,2.1, 1000)
        ss, cc = fresnel(t)
        return (self.hflip * \
                ((self.scale * cc * math.cos(self.rotation)) - \
                 (self.scale * ss * math.sin(self.rotation))) + \
                self.origin[0])

    def cosVec(self):
        t = np.linspace(0,2.1, 1000)
        ss, cc = fresnel(t)
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
        self.scan_bbox = []
        self.geom_bout_upper = None
        self.geom_bout_upper_adj = None
        self.geom_bout_middle = None
        self.geom_bout_middle_adj = None
        self.geom_bout_lower = None
        self.geom_bout_lower_adj = None
        self.geom_center_line = None
        self.geom_corner_upper_left = None
        self.geom_corner_lower_left = None
        self.geom_corner_upper_right = None
        self.geom_corner_lower_right = None

    def scan(self, imageFile, dpi=300, threshold=205, despeckle=10):
        img = Image.open(imageFile)
        img = img.convert(mode="L")

        # convert from input dots per inch to 100 dots per cm (.1mm resolution)
        resize = 2540.0/(10.0 * dpi)
        w, h = img.size
        img = img.resize((int(w * resize), int(h * resize)), Image.LANCZOS)
        img = img.point(lambda x: 0 if x < threshold else 255, '1')

        #img.show()

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

        print "Paths Scanned:", len(paths)

        #profiles = []
        #for path in paths:
        #    if len(path) > 20:
        #        profiles.append(path)
        #print "Profiles", len(profiles)
        #quit()
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
        
        assert(path.iscontinuous())

        # normalize the path for (0,0) at the centerline of the bottom of the instrument

        xmin, xmax, ymin, ymax = path.bbox()                    # use a bounding box to determine x,y extremis
        xshift = ((xmax - xmin)/2.0) + xmin                     # calculate shift to center y axis on centerline
        scale = 1000.0 / 10.0**(ceil(np.log10(ymax - ymin)))    # calculate scaling factor for pixel == 0.1mm
        path = path.translated(complex(-xshift, -ymin))         # complex translation vector
        path = path.scaled(scale)                               # scale path to 10 pixels/mm (curves get detached)
        for ix, seg in enumerate(path[:-1]):
            seg.end = path[ix+1].start                          # reattach curves so path.iscontinuous()
        path[-1].end = path[0].start

        self.scan_path = path
        self.scan_attributes = attributes
        self.scan_svg_attributes = svg_attributes               # XXX Seems not to like svg version of 1.0
        self.scan_bbox = path.bbox()

    def path_handles(self, path=None, mag=10.0):
        handles = []
        if path is None:
            path = self.scan_path

        for seg in path:
            if isinstance(seg, CubicBezier):
                vec = mag*(seg.control1 - seg.start)
                vec2 = mag*(seg.end - seg.control2)
                handles.append((seg.start,seg.start+vec))
                handles.append((seg.end,seg.end+vec))
        return handles

    def path_smooth(self, path=None):
        """Every adjoining segment starting handle and the previous segment ending handle is set to
        the average of the two handles."""
        if path is None:
            path = self.scan_path

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
        return

    def scan_compress(self, arc_thresh=2.5):
        cpath = Path()
        path = self.scan_path
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
                if (arclen > arc_thresh) or abs(ang0-ang1) > 30.0 or (ix == len(path) - 1):
                    ix1 = ix
                    p1 = complex(path[ix].end)
                    c2 = complex(path[ix].control2)
            else:
                # we have something other than a CubicBezier (note that smoothing will elimate lines if done first!)
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
        
    def geom_from_scan(self):
        """Use properties of a Viola to establish bout location and widths, corner locations, etc."""

        # first we establish the centerline
        xmin, xmax, ymin, ymax = self.scan_bbox
        self.geom_centerline = Line(complex(0,0),complex(0,ymax - ymin))

        # we need a vectorized function to find the tangent of a curve
        vf = np.vectorize(lambda t:seg.unit_tangent(t))

        bouts = []
        corners = []
        seg = self.scan_path[0]
        t_prev = np.average(vf(np.linspace(0.0,1.0,10)))
        for ix, seg in enumerate(self.scan_path):
            # Points of interest:
            #   1. Vertical lines (bouts) have curvature (0+-1j)
            #   2. Horizontal lines (top & bottom) have curvature (+-1+0j)
            #   3. Corners have segment to segment jump of curvature > .5

            t_seg = np.average(vf(np.linspace(0.0,1.0,10)))
            d_real = max(t_seg.real,t_prev.real) - min(t_seg.real,t_prev.real)
            d_imag = max(t_seg.imag,t_prev.imag) - min(t_seg.imag,t_prev.imag)
            if (abs(t_seg.real) < 0.1) and (abs(t_seg.imag) > .90):
                bouts.append(ix)
            if (abs(d_real) + abs(d_imag) > 1.0):
                corners.append(ix)
            t_prev = t_seg

        top = self.geom_centerline.end.imag
        # Find the upper left and right bout points in upper third of scan
        start, end=self.extrema_in_range(bouts,top*2.0/3.0,top)
        self.geom_bout_upper = Line(start,end)
        self.geom_bout_upper_adj = Line(complex(start.real,np.average([start.imag,end.imag])),complex(end.real,np.average([start.imag,end.imag])))

        # Find the lower left and right bout points
        start, end=self.extrema_in_range(bouts,0.0,top*1.0/3.0)
        self.geom_bout_lower = Line(start,end)
        self.geom_bout_lower_adj = Line(complex(start.real,np.average([start.imag,end.imag])),complex(end.real,np.average([start.imag,end.imag])))

        # Find the middle left and right bout points
        start, end=self.extrema_in_range(bouts,top*1.0/3.0,top*2.0/3.0, reverse=True)
        self.geom_bout_middle = Line(start,end)
        self.geom_bout_middle_adj = Line(complex(start.real,np.average([start.imag,end.imag])),complex(end.real,np.average([start.imag,end.imag])))

        # Find the lower corners
        start, end=self.extrema_in_range(corners,self.geom_bout_lower_adj.start.imag,self.geom_bout_middle_adj.start.imag)
        self.geom_corner_lower_left = start
        self.geom_corner_lower_right = end

        # Find the upper corners
        start, end=self.extrema_in_range(corners,self.geom_bout_middle_adj.start.imag,self.geom_bout_upper_adj.start.imag)
        self.geom_corner_upper_left = start
        self.geom_corner_upper_right = end

        return []

    def plot (self, plot):
        line = lambda seg,color: plot.plot([seg.start.real,seg.end.real],[seg.start.imag,seg.end.imag],color)
        point = lambda pt,color: plot.plot([pt.real],[pt.imag],color)
        line (self.geom_centerline,'r-')
        line (self.geom_bout_upper,'r-')
        line (self.geom_bout_lower,'r-')
        line (self.geom_bout_middle,'r-')
        line (self.geom_bout_upper_adj,'g-')
        line (self.geom_bout_lower_adj,'g-')
        line (self.geom_bout_middle_adj,'g-')
        point (self.geom_corner_lower_left,'b^')
        point (self.geom_corner_lower_right,'b^')
        point (self.geom_corner_upper_left,'b^')
        point (self.geom_corner_upper_right,'b^')
        for clothoid in self.clothoids:
            plot.plot(clothoid.sinVec(), clothoid.cosVec(), 'r-', linewidth=1)
        #XXX Need to calculate outline points from Bezier curves
        #plt.plot(*zip(*self.outline))

    def extrema_in_range(self,seg_list,ymin,ymax,reverse=False):
        min_point = complex(0,0)
        max_point = complex(0,0)
        if not reverse:
            min_extreme = 0.0
            max_extreme = 0.0
        else:
            min_extreme = -1.0e99   # a small number
            max_extreme = 1.0e99    # a big number

        for ix in seg_list:
            seg = self.scan_path[ix]
            # only consider segments in the selected range
            if seg.start.imag > ymin and seg.start.imag < ymax:
                t_min, t_max = bez_extrema_t(seg)
                p_min = seg.point(t_min)
                p_max = seg.point(t_max)
                if not reverse:
                    if p_min.real < min_extreme:
                        min_point = p_min
                        min_extreme = p_min.real
                    if p_max.real > max_extreme:
                        max_point = p_max
                        max_extreme = p_max.real
                else:
                    # if we are left of centerline, we want to return p_max
                    if seg.start.real < 0:
                        if p_max.real > min_extreme:
                            min_point = p_max
                            min_extreme = p_max.real
                    else:
                    # otherwise we want to return p_min
                        if p_min.real < max_extreme:
                            max_point = p_min
                            max_extreme = p_min.real
        return min_point, max_point

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
    
def bez_extrema_t(b):
    """returns the minimum and maximum for any real cubic bezier"""
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
    for t in np.linspace(0.0,1.0,10000):
        x.append(path.point(t).real)
        y.append(path.point(t).imag)
    return x,y

# Main entry point
#

with open("salo.json", 'rb') as f:
    viola = Viola.from_json(f.read())

viola.scan("clean.png")

#spath = smoothed_path(viola.scan_path, maxjointsize=100)

print "len path:", len(viola.scan_path)
print "kinks orig:", len(kinks(viola.scan_path))
path_orig = copy.deepcopy(viola.scan_path)
viola.path_smooth()
cpath = viola.scan_compress(5.0)
viola.scan_path = cpath
path_compress = copy.deepcopy(cpath)
print "kinks cpath:", len(kinks(cpath))
print "len cpath:", len(cpath)
#viola.path_smooth(cpath)
#path_smooth = cpath

#handles = viola.path_handles()

highlight = viola.geom_from_scan()

#x,y = scan_to_nodes(viola.scan_path)

plt.figure(figsize=(6,8.4))
plt.axis([-150,150,0,420])

for path, color in zip([path_orig, path_compress],['r-','b-']):
    for ix,seg in enumerate(path):
        x,y = zip(*[(seg.point(t).real,seg.point(t).imag) for t in np.linspace(0.0,1.0,10)])
        if ix in highlight:
            plt.plot(x,y,'g')
        else:
            plt.plot(x,y,color)

nodes = np.asarray(zip(viola.clothoids[0].sinVec(),viola.clothoids[0].cosVec()))
#start = timer()
for point in c.curve:
    dist_2 = np.sum((nodes - point)**2, axis=1)
    index = np.argmin(dist_2)
    a = np.array((viola.clothoids[0].sinVec()[index],  viola.clothoids[0].cosVec()[index]))
    b = np.array(point)
    plt.plot([a[0],b[0]], [a[1],b[1]], 'g-')
    print index, point, (viola.clothoids[0].sinVec()[index], viola.clothoids[0].cosVec()[index]), np.linalg.norm(a-b)
#print timer() - start

viola.plot(plt)

plt.show(block=False)
raw_input('<cr> to close program ->')

plt.close()

