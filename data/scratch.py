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

