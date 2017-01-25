import Img
import pygame
import math
import itertools
from math import pi,sin,cos,tan,asin,acos,atan
tau=pi*2 #TAU MANIFESTO
#I AM A SHAPE
def polypoints(cx,cy,r,sides,angoff=0):
    for n in xrange(sides):
        a=tau*n/sides+angoff
        yield cx+r*sin(a),cy+r*cos(a)
def star(cx,cy,r,points,ang=0,prop=0.5):
    for pos in itertools.chain(*itertools.izip(polypoints(cx,cy,r,points,ang),polypoints(cx,cy,r*prop,points,ang+pi/points))):
        yield pos