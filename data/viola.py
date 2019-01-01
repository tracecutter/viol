#!/usr/bin/env python

import csv
import json
import jsonpickle
import numpy as np
from scipy.special import fresnel
from scipy.spatial import distance
import matplotlib.pyplot as plt
import math
from svgpathtools import Path, parse_path, svg2paths, svg2paths2, wsvg
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
        self.clothoids = []
        self.outline = []

    def plot (self, plot):
        for clothoid in self.clothoids:
            plot.plot(clothoid.sinVec(), clothoid.cosVec(), 'r-', linewidth=1)
        plt.plot(*zip(*self.outline))

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
    

while True:
    with open("salo.json", 'rb') as f:
        viola = Viola.from_json(f.read())

    viola.plot(plt)

    paths, attributes, svg_attributes = svg2paths2('clean2.svg')
    xmin, xmax, ymin, ymax = paths[0].bbox()
    xshift = ((xmax - xmin)/2.0) + xmin
    scale = 0.01
    
    print xmin, xmax, ymin, ymax

    xxx = []
    yyy = []
    for t in np.linspace(.5,.999,1000):
        print paths[0].point(t).real - xshift,paths[0].point(t).imag - ymin
        xxx.append(scale * (paths[0].point(t).real-xshift))
        yyy.append(scale * (paths[0].point(t).imag-ymin))
    plt.plot(xxx,yyy,'r-')

    c = Curve(viola.outline, -150, -1, 1, 240)
    #print c

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

    plt.show(block=False)

    try:
        newA=float(raw_input('New A: '))
    except ValueError:
        break

    a[0] = newA

plt.close()

def junkOutlineCalc():
    paths, attributes, svg_attributes = svg2paths2('clean.svg')

    print paths[0]


    #  print(json.dumps(json.loads(viola.to_json()), indent=2, sort_keys=True))

    plt.figure(figsize=(6,8.4))
    #plt.axis([-150,150,0,420])
    plt.axis([0,40000,0,50000])

    xxx = []
    yyy = []
    for t in np.linspace(0,.998,1000):
        print paths[0].point(t).real,paths[0].point(t).imag
        xxx.append(paths[0].point(t).real)
        yyy.append(paths[0].point(t).imag)
    plt.plot(xxx,yyy,'r-')

    while True:
        plt.show(block=False)

        try:
            newA=float(raw_input('New A: '))
        except ValueError:
            break
        break

def junk():
    scaled_ss = h[ix]*((a[ix] * cc * math.cos(r1[ix])) - (a[ix] * ss * math.sin(r1[ix]))) + d1[ix]
    scaled_cc = v[ix]*((a[ix] * cc * math.sin(r1[ix])) + (a[ix] * ss * math.cos(r1[ix]))) + d2[ix]
    plot.plot(scaled_ss, scaled_cc, 'r-', linewidth=1)

    for n in range(len(x) - 1):
        dx = x[n+1] - x[n]
        dy = y[n+1] - y[n]
        vec = math.degrees(math.atan2(dy,dx)) - 90
        if vec < 0:
            vec+=360


        fx = h[0]*((a[0] * cc * math.cos(r1[0])) - (a[0] * ss * math.sin(r1[0]))) + d1[0]
        fy = v[0]*((a[0] * cc * math.sin(r1[0])) + (a[0] * ss * math.cos(r1[0]))) + d2[0]

        ix = int(len(fx)/2)
        ixp =0
        minerr = 1000.0

        #print fx, ix

        #while (abs(ix - ixp) > 1):
        #    err = distance.euclidean((x,y),(fx[ix],fy[ix]))
        #    print ix, x, y, fx[ix], fy[ix], err
        #    if err < minerr:
        #        minerr = err
        #    break

            #if err < last_err:
            #    n /= -2.0
            #a += d
            #l = y

