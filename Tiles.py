from Img import imgx,imgstripx,tilemapx, colcopy, RandomImageManager, UltraTiles,UTImageManager,sndget
from random import randint,choice
from copy import deepcopy
import Direction as D
switch=sndget("switch")
error=sndget("nomove")
class Tile(object):
    solid=True
    gshape=None
    img=None
    spiky=False
    spikable=False
    name="Tile"
    state=False
    unisolid=tuple()
    grav=1
    edible=False
    valuable=False
    interactive=False
    def __init__(self,x,y):
        self.x,self.y=x,y
    def re_img(self,b,lstart=True):
        pass
    def prepare(self,game):
        pass
    def on_dest(self,b):
        pass
    def eat(self,b):
        return True
    def is_face(self,dx,dy):
        if self.gshape:
            tx,ty=self.x+dx,self.y+dy
            return (tx,ty) not in ((t.x,t.y) for t in self.gshape.tiles)
        elif self.unisolid:
            return (dx,dy) in self.unisolid
        else:
            return self.solid
    def draw(self,b,screen):
        screen.blit(self.img[b.iscale],(self.x*b.scale,self.y*b.scale))
    def interact(self,b,mb):
        pass
class UltraTile(Tile):
    ut=None
    corners=(0,0,0,0)
    offcounts=True
    def re_img(self,b,lstart=True):
        corners=[]
        for dset in D.icorners:
            corner=0
            for n,(tx,ty) in enumerate(D.iter_offsets(self.x,self.y,dset)):
                if any(t.name==self.name for t in b.get_ts(tx,ty)) or not b.in_world(tx,ty):
                    corner+=n+1 if n<2 else 1
                if n==1 and corner!=3:
                    break
            corners.append(corner)
        self.corners=tuple(corners)
    @property
    def img(self):
        return self.ut[self.corners]

class Air(Tile):
    solid = False
    def draw(self,b,screen):
        pass
class Dirt(UltraTile):
    ut=UltraTiles("Tiles/Dirt")
    name="Dirt"
class Snow(UltraTile):
    ut=UltraTiles("Tiles/Snow")
    name="Snow"
class Explosion(Tile):
    img=imgx("Exp")
    name="Exp"
    def draw(self,b,screen):
        a=b.ascale
        screen.blit(self.img[b.iscale], (self.x * b.scale+randint(-a,a), self.y * b.scale+randint(-a,a)))
class WoodPlatform(Tile):
    solid = False
    unisolid = ((0,-1),)
    imgs=imgstripx("Tiles/WoodPlat")
    name="WoodPlatform"
    i=0
    def re_img(self,b,lstart=True):
        self.i=0
        for n,(tx,ty) in enumerate(D.iter_offsets(self.x,self.y,((-1,0),(1,0)))):
            for t in b.get_ts(tx,ty):
                if t.name==self.name or (t.solid and not t.gshape):
                    self.i+=2**n
                    break
    @property
    def img(self):
        return self.imgs[self.i]
class Spikes(Tile):
    imgs=tilemapx("Tiles/Spikes")
    name="Spikes"
    spiky = True
    i=0
    def re_img(self,b,lstart=True):
        self.i=0
        for n,(tx,ty) in enumerate(D.iter_offsets(self.x,self.y)):
            for t in b.get_ts(tx,ty):
                if t.solid and not t.gshape:
                    self.i+=2**n
                    break
    @property
    def img(self):
        return self.imgs[self.i]
class Portal(Tile):
    name="Portal"
    imgs=imgstripx("Tiles/Portal")
    i=0
    solid = False
    def re_img(self,b,lstart=True):
        self.i=not b.fruit
    @property
    def img(self):
        return self.imgs[self.i]
def fruit_col():
    while True:
        fruitcol=(randint(0,255),randint(0,255),randint(0,128))
        if max(fruitcol)-min(fruitcol)>128:
            return fruitcol
IM_FRUIT=RandomImageManager(imgstripx("Fruit"),fruit_col)
IM_BLOCK=UTImageManager("Tiles/GravBlock",lambda:(randint(50,150),randint(50,150),randint(50,150)))
class Fruit(Tile):
    name = "Fruit"
    imgs=imgstripx("Fruit")
    edible = True
    def __init__(self,x,y):
        Tile.__init__(self,x,y)
        self.iid=IM_FRUIT.register()
    def eat(self,b):
        b.fruit-=1
        return True
    @property
    def state(self):
        return "Fruit"+str((self.x,self.y))
    @property
    def img(self):
        return IM_FRUIT[self.iid]
class XBlock(Tile):
    imgs=imgstripx("Tiles/XBlock")
    name="XBlock"
    def __init__(self,x,y,active=False):
        Tile.__init__(self,x,y)
        self.active=active
    @property
    def img(self):
        return self.imgs[self.active]
    @property
    def solid(self):
        return self.active
    @property
    def state(self):
        return "XB"+"A" if self.active else ""
class XButton(Tile):
    img=imgx("Tiles/XButton")
    interactive = True
    def interact(self,b,mb):
        xbs=[]
        for t in b.itertiles():
            if t.name=="XBlock":
                if not any((ot.solid for ot in b.get_ts(t.x,t.y) if not ot is t)):
                    xbs.append(t)
                else:
                    error.play()
                    return False
        for x in xbs:
            x.active=not x.active
        if xbs:
            switch.play()
            return True
class GravShape(object):
    def __init__(self,*tiles):
        self.tiles=list(tiles)
class BGravShape(GravShape):
    def __init__(self):
        self.iid=IM_BLOCK.register()
        self.tiles=[]
class Block(UltraTile):
    def __init__(self,x,y,gshape):
        UltraTile.__init__(self,x,y)
        self.gshape=gshape
        gshape.tiles.append(self)
    def re_img(self, b, lstart=True):
        corners = []
        for dset in D.icorners:
            corner = 0
            for n, (tx, ty) in enumerate(D.iter_offsets(self.x, self.y, dset)):
                for t in b.get_ts(tx, ty):
                    if t in self.gshape.tiles:
                        corner += n + 1 if n < 2 else 1
                        break
                if n == 1 and corner != 3:
                    break
            corners.append(corner)
        self.corners = tuple(corners)
    def on_dest(self,b):
        self.gshape.tiles.remove(self)
        for t in self.gshape.tiles:
            t.re_img(b,False)
    @property
    def ut(self):
        return IM_BLOCK[self.gshape.iid]
class CloudBlock(Block):
    ut=UltraTiles("Tiles/CloudBlock")
    grav=0
class SpikeBlock(Block):
    ut=UltraTiles("Tiles/SpikeBlock")
    spiky = True
class Cheese(Block):
    ut=UltraTiles("Tiles/Cheese")
    edible = True
    def eat(self,b):
        return False