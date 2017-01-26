import Img
from random import randint,choice,random,uniform
from Graphics import tau,star,seaweed
from math import pi,sin,cos,tan,asin,acos,atan
import pygame
class FXLayer(object):
    def __init__(self,fxs=None):
        if fxs is None:
            self.fxs=[]
        else:
            self.fxs=fxs
    def update(self,b):
        pass
    def render(self,ss,b):
        self.update(b)
        for fx in self.fxs[:]:
            if fx.render(ss,b):
                self.fxs.remove(fx)
class RFXLayer(FXLayer):
    def __init__(self,fx,density,b,hoz=True):
        self.d=density
        self.fx=fx
        self.h=hoz
        FXLayer.__init__(self)
        for x in xrange(b.sx):
            for y in xrange(b.sy*b.rscale):
                if random() < self.d:
                    self.fxs.append(self.fx(b,y))
    def update(self,b):
        for _ in xrange(b.sx if self.h else b.sy):
            if random()<self.d:
                self.fxs.append(self.fx(b))
class DFXLayer(FXLayer):
    def __init__(self,fx,density,b,i_x=False,i_y=False):
        self.d=density
        self.fx=fx
        FXLayer.__init__(self)
        for _ in xrange((1 if i_x else b.sx)*(1 if i_y else b.sy)):
            if random() < self.d:
                self.fxs.append(self.fx(b))
class FX(object):
    x=0
    y=0
    def render(self,ss,b):
        pass
    def rpos(self,b):
        return tuple(p*b.ascale//4 for p in (self.x,self.y))
class ImgFX(FX):
    img=None
    def update(self,b):
        pass
    def render(self,ss,b):
        ss.blit(self.img[b.iscale],self.rpos(b))
        return self.update(b)
class Mountain(ImgFX):
    imgs=[Img.imgx("FX/"+s+"Mountain") for s in ("Small","Double","Tall")]
    def __init__(self,b):
        self.i=randint(0,2)
        self.x=randint(0-self.img.w*4,b.sx*64)
        self.y=b.sy*64-self.img.h*4
    @property
    def img(self):
        return self.imgs[self.i]
class Snow(ImgFX):
    img=Img.imgx("FX/Snow")
    s=24
    def __init__(self,b,y=0):
        self.x=randint(-64,b.sx*64+64)
        self.y=y-self.s
    def update(self,b):
        self.y+=uniform(1,1.2)
        self.x+=uniform(-1,1)
        if self.y>=b.sy*64:
            return True
class RFX(FX):
    col=(0,0,0)
    points=()
    def render(self,ss,b):
        pygame.draw.polygon(ss,self.col,[tuple(p*b.ascale//4 for p in (px,py)) for px,py in self.points])
class Star(RFX):
    col=(255,)*3
    def __init__(self,b):
        self.points=list(star(randint(0,b.sx*64),randint(0,b.sy*64),randint(16,32),randint(5,7),uniform(0,tau),uniform(0.6,0.3)))
class RotoStar(Star):
    def __init__(self,b):
        self.args=[randint(0,b.sx*64),randint(0,b.sy*64),randint(16,32),randint(5,7),0,uniform(0.6,0.3)]
        self.r=uniform(0,tau)
        self.rs=uniform(-0.05,0.05)
    @property
    def points(self):
        self.r+=self.rs
        self.r%=tau
        self.args[4]=self.r
        return list(star(*self.args))
class BeamFX(FX):
    def __init__(self,b):
        self.ba=uniform(0.01,0.02)
        self.sx=randint(0,b.sx*b.rscale)
        self.r=uniform(pi/12,pi/8)
        self.speed=uniform(0.01,0.02)
        self.sw=uniform(0,tau)
        self.col=choice(((255,255,0),(255,0,255),(0,255,255),(255,0,0),(0,255,0),(0,0,255)))
    def render(self,ss,b):
        self.sw+=self.speed
        self.sw%=tau
        ang=pi/2+self.r*sin(self.sw)
        h=b.sy*b.rscale
        pygame.draw.polygon(ss,self.col,((self.sx,h),(self.sx+h/tan(ang-self.ba),0),(self.sx+h/tan(ang+self.ba),0)))
class Seaweed(RFX):
    col=(75,127,75)
    def __init__(self,b):
        self.base=randint(0,b.sx*64)
        self.segs=randint(5,10)
        self.segl=randint(32,48)
        self.wav=uniform(0.1,0.3)
        self.wavw=randint(4,8)
        self.prog=uniform(0,tau)
        self.speed=uniform(0.01,0.02)
        self.w=randint(4,8)
        self.h=b.sy*64
        self.csegs=[tuple(c+randint(-10,10) for c in self.col) for _ in range(self.segs)]
    @property
    def points(self):
        self.prog+=self.speed
        self.prog%=tau
        return seaweed(self.base,self.segs,self.segl,self.wav,self.wavw,self.prog,self.w,self.h)
    def render(self,ss,b):
        for n,pset in enumerate(self.points):
            pygame.draw.polygon(ss,self.csegs[n],[tuple(p*b.ascale//4 for p in (px,py)) for px,py in pset])
class BackSnow(Snow):
    s=12
    img = Img.imgx("FX/SmallSnow")

