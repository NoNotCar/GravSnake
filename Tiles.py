from random import randint

import Direction as D
import Img
from Img import imgx,imgstripx,tilemapx, RandomImageManager, UltraTiles,UTImageManager

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
    connective=False
    def __init__(self,x,y):
        self.x,self.y=x,y
    def re_img(self,b,lstart=True):
        pass
    def prepare(self,game):
        pass
    def on_dest(self,b):
        pass
    def eat(self, b, snake):
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
    def on_select(self,b):
        pass
    def on_deselect(self,b):
        pass
    def on_portal(self,b):
        pass
    def same(self, other):
        if isinstance(other,Tile):
            return self.name==other.name
        return False
class SBlockTile(Tile):
    def __init__(self,x,y):
        Tile.__init__(self,x,y)
        self.gshape=GravShape(self)
class RotatableTile(Tile):
    imgs=()
    def __init__(self,x,y,r=0):
        Tile.__init__(self,x,y)
        self.r=r
    @property
    def img(self):
        return self.imgs[self.r]
class UltraTile(Tile):
    ut=None
    corners=(0,0,0,0)
    offcounts=True
    def re_img(self,b,lstart=True):
        corners=[]
        for dset in D.icorners:
            corner=0
            for n,(tx,ty) in enumerate(D.iter_offsets(self.x,self.y,dset)):
                if any(self.same(t) for t in b.get_ts(tx,ty)) or not b.in_world(tx,ty):
                    corner+=n+1 if n<2 else 1
                if n==1 and corner!=3:
                    break
            corners.append(corner)
        self.corners=tuple(corners)
    @property
    def img(self):
        return self.ut[self.corners]
class Terrain(UltraTile):
    connective = True
class Dirt(Terrain):
    ut=UltraTiles("Tiles/Dirt")
    name="Dirt"
class PinkDirt(Terrain):
    ut=UltraTiles("Tiles/PinkDirt")
    name="PinkDirt"
class Snow(Terrain):
    ut=UltraTiles("Tiles/Snow")
    name="Snow"
class SeaBlock(Terrain):
    ut=UltraTiles("Tiles/SeaBlock")
    name="SeaBlock"
class Asteroid(Terrain):
    ut=UltraTiles("Tiles/Asteroid")
    name="Asteroid"
class Hex(UltraTile):
    uts=imgs=[Img.UltraTiles("Tiles/Hex", col) for col in cols]
    for n,u in enumerate(uts):
        for il in u.tiles:
            for i in il:
                Img.colswap(i, (192, 192, 192), Img.darker(cols[n]))
    name="Hex"
    def __init__(self,x,y,col=0):
        UltraTile.__init__(self,x,y)
        self.col=col
    @property
    def ut(self):
        return self.uts[self.col]
    def same(self, other):
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
    img=imgx("Tiles/WoodPlat")
    name="WoodPlatform"
class Spikes(Tile):
    imgs=tilemapx("Tiles/Spikes")
    name="Spikes"
    spiky = True
    i=0
    connective = True
    def re_img(self,b,lstart=True):
        self.i=0
        for n,(tx,ty) in enumerate(D.iter_offsets(self.x,self.y)):
            for t in b.get_ts(tx,ty):
                if t.connective:
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
    def eat(self, b, snake):
        b.fruit-=1
        return True
    @property
    def state(self):
        return "Fruit"+str((self.x,self.y))
    @property
    def img(self):
        return IM_FRUIT[self.iid]
class Fluffy(Tile):
    #EAT FLUFFY GET FLIPPY
    name = "Fluffy"
    img = imgx("Fluffy")
    edible = True
    def eat(self, b, snake):
        snake.snake.grav=-snake.snake.grav
        return False
    @property
    def state(self):
        return "Fluffy"
class GravShape(object):
    def __init__(self,*tiles):
        self.tiles=list(tiles)
class BGravShape(GravShape):
    def __init__(self):
        self.iid=IM_BLOCK.register()
        self.tiles=[]
class Block(UltraTile):
    name="Block"
    extension=None
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
    def move(self,dx,dy,b):
        return self.extension.move(dx,dy,b)
    @property
    def ut(self):
        return IM_BLOCK[self.gshape.iid]
    @property
    def state(self):
        return "B"+str((self.x,self.y))
    @property
    def interactive(self):
        if self.extension:
            return self.extension.interactive
        return 0
    def draw(self,b,screen):
        UltraTile.draw(self,b,screen)
        if self.extension:
            screen.blit(self.extension.img[b.iscale], (self.x * b.scale, self.y * b.scale))
class CloudBlock(Block):
    ut=UltraTiles("Tiles/CloudBlock")
    grav=0
class SpikeBlock(Block):
    ut=UltraTiles("Tiles/SpikeBlock")
    spiky = True
class Cheese(Block):
    ut=UltraTiles("Tiles/Cheese")
    edible = True
    def eat(self, b, snake):
        return False
class Diamond(Tile):
    img=imgx("Diamond")
    portals = True
    goal = True
    valuable = True
    def __init__(self,x,y):
        Tile.__init__(self,x,y)
        self.gshape=GravShape(self)
class OnceGoalBlock(RotatableTile):
    imgs= Img.imgrot(Img.imgx("Tiles/1TGoal"))
    ct= Img.imgstripx("CrossTick")
    goal = True
    sat=False
    def satisfied(self,b):
        if self.sat:
            return True
        for t in b.get_ts(*D.add_vs((self.x,self.y),D.get_dir(self.r))):
            if t.solid:
                self.sat=True
                return True
    def draw(self,b,screen):
        RotatableTile.draw(self,b,screen)
        screen.blit(self.ct[self.sat][b.iscale], (self.x * b.scale, self.y * b.scale))
