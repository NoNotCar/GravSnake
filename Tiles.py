from Img import imgx,imgstripx,tilemapx, RandomImageManager, UltraTiles,UTImageManager
import Img
from random import randint,choice
from copy import deepcopy
import Direction as D
cols=[(255,0,0),(0,0,255),(255,255,0),(0,255,0)]
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
    goal=False
    portals=False
    interactive=False
    selected=False
    pushdirs=[]
    updates=False
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
    def push(self,b):
        pass
    def satisfied(self,b):
        return False
    def move(self,dx,dy,b):
        return False
    def update(self,b):
        pass
    def pre_grav(self,b):
        return self.update(b)
    def post_grav(self,b):
        return self.update(b)
    def __eq__(self, other):
        if isinstance(other,Tile):
            return self.name==other.name
        return False
class UltraTile(Tile):
    ut=None
    corners=(0,0,0,0)
    offcounts=True
    def re_img(self,b,lstart=True):
        corners=[]
        for dset in D.icorners:
            corner=0
            for n,(tx,ty) in enumerate(D.iter_offsets(self.x,self.y,dset)):
                if any(t==self for t in b.get_ts(tx,ty)) or not b.in_world(tx,ty):
                    corner+=n+1 if n<2 else 1
                if n==1 and corner!=3:
                    break
            corners.append(corner)
        self.corners=tuple(corners)
    @property
    def img(self):
        return self.ut[self.corners]
class Dirt(UltraTile):
    ut=UltraTiles("Tiles/Dirt")
    name="Dirt"
class Snow(UltraTile):
    ut=UltraTiles("Tiles/Snow")
    name="Snow"
class Hex(UltraTile):
    uts=imgs=[Img.UltraTiles("Tiles/Hex",col) for col in cols]
    for n,u in enumerate(uts):
        for il in u.tiles:
            for i in il:
                Img.colswap(i,(192,192,192),Img.darker(cols[n]))
    name="Hex"
    def __init__(self,x,y,col=0):
        UltraTile.__init__(self,x,y)
        self.col=col
    @property
    def ut(self):
        return self.uts[self.col]
    def __eq__(self, other):
        if isinstance(other,Hex):
            return self.col==other.col
        return False
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
class Diamond(Tile):
    img=imgx("Diamond")
    portals = True
    goal = True
    valuable = True
    def __init__(self,x,y):
        Tile.__init__(self,x,y)
        self.gshape=GravShape(self)