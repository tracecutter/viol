import csv
import numpy as np
from scipy.special import fresnel
import matplotlib.pyplot as plt
import math

a  = [210,148,45,68,36,48.4,163,107,210,148,45,68,36,48.4,163,107]
r1 = [-2.434,0.0,1.05,-1.455,1.756,1.2,0.83,0.0,-2.434,0.0,1.05,-1.455,1.756,1.2,0.83,0.0]
d1 = [-37,0,-107,-60,-60.5,-87,-37,0,37,0,107,60,60.5,87,37,0]
d2 = [205,0,127,212,240,302,223,382.5,205,0,127,212,240,302,223,382.5]
h  = [1,-1,1,-1,1,1,-1,-1,-1,1,-1,1,-1,-1,1,1]
v  = [1,1,1,1,1,-1,1,-1,1,1,1,1,1,-1,1,-1]

t = np.linspace(0,2.1, 1000)
ss, cc = fresnel(t)

while True:
    plt.figure(figsize=(6,8.4))
    plt.axis([-150,150,0,420])

    for ix in range(len(a)):
        scaled_ss = h[ix]*((a[ix] * cc * math.cos(r1[ix])) - (a[ix] * ss * math.sin(r1[ix]))) + d1[ix]
        scaled_cc = v[ix]*((a[ix] * cc * math.sin(r1[ix])) + (a[ix] * ss * math.cos(r1[ix]))) + d2[ix]
        plt.plot(scaled_ss, scaled_cc, 'r-', linewidth=1)

    x = []
    y = []

    with open('outline.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            x.append (float(row[0]))
            y.append (float(row[1]))
            
    plt.plot(x,y)
    plt.show(block=False)

    try:
        newA=float(raw_input('New A: '))
    except ValueError:
        break

    a[0] = newA

plt.close()
