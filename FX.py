import Img
from random import randint,choice,random,uniform
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
            for y in xrange(b.sy*64):
                if random() < self.d:
                    self.fxs.append(self.fx(b,y))
    def update(self,b):
        for _ in xrange(b.sx if self.h else b.sy):
            if random()<self.d:
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
class BackSnow(Snow):
    s=12
    img = Img.imgx("FX/SmallSnow")

