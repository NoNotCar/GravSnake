from Img import imgx,imgstripx,tilemapx, colcopy, RandomImageManager, UltraTiles,UTImageManager
from random import randint,choice
from copy import deepcopy
import Direction as D
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
    def __init__(self,x,y):
        self.x,self.y=x,y
    def re_img(self,b,lstart=True):
        pass
    def prepare(self,game):
        pass
    def on_dest(self,b):
        pass
    def is_face(self,dx,dy):
        if self.gshape:
            tx,ty=self.x+dx,self.y+dy
            return (tx,ty) not in ((t.x,t.y) for t in self.gshape.tiles)
        elif self.unisolid:
            return (dx,dy) in self.unisolid
        else:
            return self.solid
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
class Dirt(UltraTile):
    ut=UltraTiles("Tiles/Dirt")
    name="Dirt"
class Snow(UltraTile):
    ut=UltraTiles("Tiles/Snow")
    name="Snow"
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
    def __init__(self,x,y):
        Tile.__init__(self,x,y)
        self.iid=IM_FRUIT.register()
    @property
    def state(self):
        return "Fruit"+str((self.x,self.y))
    @property
    def img(self):
        return IM_FRUIT[self.iid]
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