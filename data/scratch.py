Slice out and plot a piece of a path in green
#slice out a portion of the path
path = path_slice(viola.outline_path,
           viola.outline_feature_corner_lower_left.T,
           viola.outline_feature_turn_lower_left.T)

x,y = zip(*[(path.point(T).real,path.point(T).imag) for T in np.linspace(0.0,1.0,500)])
plt.plot(x,y,'g-')


Load a pickled Viola
#with open("salo.json", 'rb') as f:
#    viola = Viola.from_json(f.read())

Digitize a path (the clunky way)
def scan_to_nodes(path):
    x = []
    y = []
    for t in np.linspace(0.0,1.0,10000):
        x.append(path.point(t).real)
        y.append(path.point(t).imag)
    return x,y

Examine the number of profiles found in scan
#profiles = []
#for path in paths:
#    if len(path) > 20:
#        profiles.append(path)
#print "Profiles", len(profiles)
#quit()

Some experiments on graphing curvature with linear fits
#t_vec = np.array(np.linspace(0.0,1.0,10))
#phase = [cmath.phase(complex(math.sin(cmath.pi*T**2/2.0),math.cos(cmath.pi*T**2/2.0))) for T in t_vec]

#z = np.polyfit(t_vec, phase, 1)
#p = np.poly1d(z)
#print z
#print p

#plt.figure(figsize=(12,6))
#plt.axis([0,3.141,-cmath.pi,cmath.pi])
#plt.axis([0,1.0,-cmath.pi,cmath.pi])
#plt.axis([0,1.0,0,0.5])
#plt.plot(ss, cc, 'r-', linewidth=1)
#plt.plot(t_vec,c,'b-')
#plt.plot(t_vec,phase,'b-')
#plt.plot(t_vec,p(t_vec),'r-')

#ss, cc = fresnel(t_vec)
#t_vec = np.array(np.linspace(0.0,1.0,10))
#phase = [cmath.phase(complex(math.sin(cmath.pi*T**2/2.0),math.cos(cmath.pi*T**2/2.0))) for T in t_vec]


Find t for unit_tangent on Eulers Curve
# find location t on Euler's Curve where the tangent is 45 degrees (note that this is also sin(45degrees)!
# In normalized fresnel integral the form is (integral(sin((pi/2)*t**2)),integral(cos((pi/2)*t**2))
# The unit vector on a normalized fresnel integral is (cos((pi/2)*t**2),sin((pi/2)*t**2))
# In t = sqrt(2 * desired_phi/cmath.pi)
# f = lambda t: abs(cmath.phase(complex(math.sin((cmath.pi/2.0)*t**2),math.cos((cmath.pi/2.0)*t**2)))-(cmath.pi/4.0))
#t = minimize_scalar(f, bounds=(0, 1.0), method='bounded', options={'xatol': 1e-5,'disp':3}).x
#print t, fresnel(t), 2**-0.5

#print math.degrees(cmath.phase(viola.outline_feature_turn_lower_left.tangent()))

#plot.plot(clothoid.sinVec(), clothoid.cosVec(), 'r-', linewidth=1)

#c = [(path.curvature(T)) for T in t_vec]
#phase = [cmath.phase(path.unit_tangent(T)) for T in t_vec]
#phase = [cmath.phase(path.point(T+.01) - path.point(T)) for T in t_vec]

# normalization of fresnel integrals
# In a normalized fresnel integral, phi = t**2
    def sinVec(self):
        t = np.linspace(0,2.1, 1000)
        ss, cc = fresnel(t/(math.sqrt(math.pi/2)))
        ss = ss * math.sqrt(math.pi / 2)
        cc = cc * math.sqrt(math.pi / 2)
        return (self.hflip * \
                ((self.scale * cc * math.cos(self.rotation)) - \
                 (self.scale * ss * math.sin(self.rotation))) + \
                self.origin[0])

    def cosVec(self):
        t = np.linspace(0,2.1, 1000)
        ss, cc = fresnel(t/(math.sqrt(math.pi/2)))
        ss = ss * math.sqrt(math.pi / 2)
        cc = cc * math.sqrt(math.pi / 2)
        return (self.vflip * \
                ((self.scale * cc * math.sin(self.rotation)) + \
                 (self.scale * ss * math.cos(self.rotation))) + \
                self.origin[1])
#an attempt to find t at unit_tangent angle
t = math.asin(cmath.pi/4)**0.5
print t, fresnel(t)
quit()

# verify t and arclen grow proportionally
alen = 0.0
t_vec2 = [0]
y_vec2 = [0]
for seg in path:
    alen = alen + seg.length()
    t_vec2.append(path.t2T(seg,1.0))
    y_vec2.append(cmath.phase(seg.unit_tangent(1.0)))
    #y_vec2.append(alen/path.length())

#slice out a portion of the path
path = path_slice(viola.outline_path,
           viola.outline_feature_turn_lower_left.T,
           viola.outline_feature_centerline.bot.T)

x,y = zip(*[(path.point(T).real,path.point(T).imag) for T in np.linspace(0.0,1.0,5000)])
plt.plot(x,y,'g-')


#find nearest point to clothoid
nodes = np.asarray(zip(viola.clothoids[0].sinVec(),viola.clothoids[0].cosVec()))
start = timer()
for point in c.curve:
    dist_2 = np.sum((nodes - point)**2, axis=1)
    index = np.argmin(dist_2)
    a = np.array((viola.clothoids[0].sinVec()[index],  viola.clothoids[0].cosVec()[index]))
    b = np.array(point)
    plt.plot([a[0],b[0]], [a[1],b[1]], 'g-')
    print index, point, (viola.clothoids[0].sinVec()[index], viola.clothoids[0].cosVec()[index]), np.linalg.norm(a-b)
print timer() - start

#plot multiple paths

for path, color in zip([path_orig, path_compress],['r-','b-']):
    for ix,seg in enumerate(path):
        x,y = zip(*[(seg.point(t).real,seg.point(t).imag) for t in np.linspace(0.0,1.0,10)])
        plt.plot(x,y,color)

#print "len path:", len(viola.outline_path)
#print "kinks orig:", len(kinks(viola.outline_path))
#path_orig = copy.deepcopy(viola.outline_path)
#viola.path_smooth()
#cpath = viola.outline_path_compress(5.0)
#viola.outline_path = cpath
#path_compress = copy.deepcopy(cpath)
#print "kinks cpath:", len(kinks(cpath))
#print "len cpath:", len(cpath)
#viola.path_smooth(cpath)
#path_smooth = cpath

#handles = viola.path_handles()
#x,y = scan_to_nodes(viola.outline_path)
        #t2p = lambda T: (self.outline_path.point(T).real,self.outline_path.point(T).imag)
        #line = lambda x0,y0,x1,y1,color: plot.plot([x0,x1],[y0,y1],color)
        #point = lambda x0,y0,color: plot.plot([x0],[y0],color)

        #print self.outline_feature_turn_upper_left
        #print self.outline_feature_turn_lower_left
        #print self.outline_feature_turn_lower_right
        #print self.outline_feature_turn_upper_right
        #print self.outline_feature_bout_lower
        #print self.outline_feature_corner_lower_left
        #print self.outline_feature_corner_lower_right
        #print self.outline_feature_bout_middle
        #print self.outline_feature_corner_upper_left
        #print self.outline_feature_corner_upper_right
        #print self.outline_feature_bout_upper

#computing a horizontal bout
        self.geom_bout_upper_adj = Line(complex(start.real,np.average([start.imag,end.imag])),complex(end.real,np.average([start.imag,end.imag])))

#for ix in range(0, len(handles)-1,2):
    #plt.plot([handles[ix][0].real,handles[ix][1].real],[handles[ix][0].imag,handles[ix][1].imag],'r-')
    #plt.plot([handles[ix+1][0].real,handles[ix+1][1].real],[handles[ix+1][0].imag,handles[ix+1][1].imag],'b-')

                #XXX Print the relative magnitude of handles to arc length
                #c1_mag = complex(path[ix].control1) - complex(path[ix].start)
                #c1_mag = (c1_mag.real**2 + c1_mag.imag**2)**.5
                #print "C1 relative magnitude:", c1_mag, c1_mag/path[ix].length()

#a clunky way to plot a segment
#x = []
#y = []
#for t in np.linspace(0.0,1.0,10):
#    x.append(seg.point(t).real)
#    y.append(seg.point(t).imag)

#plt.plot(x,y,'r-', linewidth=2.0)

#x,y = scan_to_nodes(cpath)
#plt.plot(x,y,'b-', linewidth=.5)

#plt.show(block=True)
#quit()

# ploting a point
#plt.plot (x,y, 'bo', ms=2.0)

# computing average curvature
#t_vec = np.array(np.linspace(0.0,1.0,10))
#vf = np.vectorize(lambda t:seg.curvature(t))
#print ix, np.average(vf(t_vec))

# incremental drawing
#plt.draw()
#plt.pause(.1)
#plt.show(block=False)
#raw_input('<cr> next segment->')

        #disvg([path], 'g')
        #quit()
        #del(viola.scan_path[:550])
        #del(viola.scan_path[3:])
            if (pt.imag > 0) and isinstance(seg, CubicBezier) and (pt.real/pt.imag) < .05:
                if False:
                    if (pt.real >= 0) and (pt.imag > 0) and prev == "2":
                        prev = "1"
                    if (pt.real >= 0) and (pt.imag > 0) and prev == "4":
                        prev = "1"
                    if (pt.real < 0) and (pt.imag >= 0) and prev == "1":
                        prev = "2"
                    if (pt.real < 0) and (pt.imag < 0) and prev == "2":
                        prev = "3"
                    if (pt.real >= 0) and (pt.imag < 0) and prev == "3":
                        prev = "4"
                    if (pt.real >= 0) and (pt.imag < 0) and prev == "1":
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

try:
    newA=float(raw_input('New A: '))
except ValueError:
    break

a[0] = newA

def junkOutlineCalc():
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

    paths, attributes, svg_attributes = svg2paths2('clean.svg')

    print paths[0]


    #  print(json.dumps(json.loads(viola.to_json()), indent=2, sort_keys=True))

    plt.figure(figsize=(6,8.4))
    plt.axis([-150,150,0,420])
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
    scaled_ss = h[ix]*((a[ix] * cc * cos(r1[ix])) - (a[ix] * ss * sin(r1[ix]))) + d1[ix]
    scaled_cc = v[ix]*((a[ix] * cc * sin(r1[ix])) + (a[ix] * ss * cos(r1[ix]))) + d2[ix]
    plot.plot(scaled_ss, scaled_cc, 'r-', linewidth=1)

    for n in range(len(x) - 1):
        dx = x[n+1] - x[n]
        dy = y[n+1] - y[n]
        vec = degrees(atan2(dy,dx)) - 90
        if vec < 0:
            vec+=360


        fx = h[0]*((a[0] * cc * cos(r1[0])) - (a[0] * ss * sin(r1[0]))) + d1[0]
        fy = v[0]*((a[0] * cc * sin(r1[0])) + (a[0] * ss * cos(r1[0]))) + d2[0]

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

Draw bezier handles
    def path_handles(self, path=None, mag=10.0):
        handles = []
        if path is None:
            path = self.outline_path

        for seg in path:
            if isinstance(seg, CubicBezier):
                vec = mag*(seg.control1 - seg.start)
                vec2 = mag*(seg.end - seg.control2)
                handles.append((seg.start,seg.start+vec))
                handles.append((seg.end,seg.end+vec))
        return handles

