import Img
import Direction as D
import pickle
class Terrain(object):
    ut=None
    corners=(0,0,0,0)
    name="Terrain"
    def re_img(self,wm,x,y):
        corners = []
        for dset in D.icorners:
            corner = 0
            for n, (tx, ty) in enumerate(D.iter_offsets(x, y, dset)):
                if wm.in_world(tx,ty):
                    t=wm.get_t(tx,ty)
                    if t and t.name==self.name:
                        corner += n + 1 if n < 2 else 1
                else:
                    corner += n + 1 if n < 2 else 1
                if n == 1 and corner != 3:
                    break
            corners.append(corner)
        self.corners = tuple(corners)
    @property
    def img(self):
        return self.ut[self.corners]
class Dirt(Terrain):
    ut=Img.UltraTiles("Tiles/WMapDirt")
    name="Dirt"
class PinkDirt(Terrain):
    ut=Img.UltraTiles("Tiles/WMapPinkDirt")
    name="PinkDirt"
class Snow(Terrain):
    ut=Img.UltraTiles("Tiles/WMapSnow")
    name="Snow"
class Path(object):
    ut = Img.UltraTiles("WMapPath")
    but=Img.UltraTiles("WMapBridge")
    bbits=Img.imgstripx("BridgeBit")
    eimg=ut[(0,0,0,0)]
    corners = (0, 0, 0, 0)
    revealed=1
    progress=1
    bridge=False
    bridgeends=(0,0,0,0)
    name="Path"
    def re_img(self, wm, x, y):
        self.bridge=not wm.get_t(x,y)
        if not self.bridge:
            self.bridgeends = [0, 0, 0, 0]
            for n, (tx, ty) in enumerate(D.iter_offsets(x, y)):
                p=wm.get_p(tx,ty)
                if p and p.revealed:
                    self.bridgeends[n]=not wm.get_t(tx,ty)
        corners = []
        for dset in D.icorners:
            corner = 0
            for n, (tx, ty) in enumerate(D.iter_offsets(x, y, dset)):
                if wm.in_world(tx, ty):
                    p = wm.get_p(tx, ty)
                    if p and p.revealed:
                        corner += n + 1 if n < 2 else 1
                if n == 1:
                    break
            corners.append(corner)
        self.corners = tuple(corners)
    @property
    def img(self):
        return (self.but if self.bridge else self.ut)[self.corners]
    def draw(self,x,y,ss,b):
        if self.revealed:
            ss.blit(self.img[b.iscale],(x*b.rscale,y*b.rscale))
            if not self.bridge:
                for n,br in enumerate(self.bridgeends):
                    if br:
                        ss.blit(self.bbits[n][b.iscale], (x * b.rscale, y * b.rscale))
class Spawn(Path):
    limg=Img.imgx("WMapGo")
    eimg=limg
    progress=1
    def draw(self,x,y,ss,b):
        Path.draw(self,x,y,ss,b)
        ss.blit(self.limg[b.iscale], (x * b.rscale, y * b.rscale))
class Level(Spawn):
    progress=0
    limgs=Img.imgstripx("WMapLevels")
    eimg = limgs[2]
    stop = True
    name="Level"
    def __init__(self,lname):
        self.lname=lname
        with open(Img.np(Img.loc + "Levels/%s.lvl" % lname)) as s:
            self.b = pickle.load(s)
    @property
    def limg(self):
        return self.limgs[self.progress+self.revealed]
    def draw(self,x,y,ss,b):
        Path.draw(self, x, y, ss, b)
        if self.revealed:
            ss.blit(self.limg[b.iscale], (x * b.rscale, y * b.rscale))
        if not b.game:
            Img.bcentrepos(Img.sfont,self.lname,ss,(x*b.rscale+b.rscale//2,y*b.rscale))
