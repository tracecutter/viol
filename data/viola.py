#!/usr/bin/env python

import csv
import json
import jsonpickle
import numpy as np
from scipy.special import fresnel
from scipy.spatial import distance
import matplotlib.pyplot as plt
import math

"""
a  = [210,148,45,68,36,48.4,163,107,210,148,45,68,36,48.4,163,107]
r1 = [-2.434,0.0,1.05,-1.455,1.756,1.2,0.83,0.0,-2.434,0.0,1.05,-1.455,1.756,1.2,0.83,0.0]
d1 = [-37,0,-107,-60,-60.5,-87,-37,0,37,0,107,60,60.5,87,37,0]
d2 = [205,0,127,212,240,302,223,382.5,205,0,127,212,240,302,223,382.5]
h  = [1,-1,1,-1,1,1,-1,-1,-1,1,-1,1,-1,-1,1,1]
v  = [1,1,1,1,1,-1,1,-1,1,1,1,1,1,-1,1,-1]
"""

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



while True:
    """
    clist = [
            Clothoid(210,-2.434,(-37,205),1,1),
            Clothoid(148,0,(0,0),-1,1),
            Clothoid(45,1.05,(-107,127),1,1),
            Clothoid(68,-1.455,(-60,212),-1,1),
            Clothoid(36,1.756,(-60.5,240),1,1),
            Clothoid(48.4,1.2,(-87,302),1,-1),
            Clothoid(163,0.83,(-37,223),-1,1),
            Clothoid(107,0,(0,382.5),-1,-1),
            Clothoid(210,-2.434,(37,205),-1,1),
            Clothoid(148,0,(0,0),1,1),
            Clothoid(45,1.05,(107,127),-1,1),
            Clothoid(68,-1.455,(60,212),1,1),
            Clothoid(36,1.756,(60.5,240),-1,1),
            Clothoid(48.4,1.2,(87,302),-1,-1),
            Clothoid(163,0.83,(37,223),1,1),
            Clothoid(107,0,(0,382.5),1,-1)]
    """

    with open("salo.json", 'rb') as f:
        viola = Viola.from_json(f.read())

    """
    viola.clothoids = clist

    with open("outline.csv", 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            viola.outline.append ((float(row[0]), float(row[1])))

    with open("salo.json", 'wb') as f:
        f.write(viola.to_json())
    """

    print(json.dumps(json.loads(viola.to_json()), indent=2, sort_keys=True))

    plt.figure(figsize=(6,8.4))
    plt.axis([-150,150,0,420])

    viola.plot(plt)

    plt.show(block=False)

    try:
        newA=float(raw_input('New A: '))
    except ValueError:
        break

    a[0] = newA

plt.close()

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

