import Direction as D
import Img
from Tiles import Tile,Block,GravShape

switch= Img.sndget("switch")
error= Img.sndget("nomove")
stick= Img.sndget("stick")
thud= Img.sndget("thud")
cols=[(255,0,0),(0,0,255),(255,255,0),(0,255,0)]
def xswitch(b,col):
    xbs = []
    for t in b.itertiles():
        if t.name in ("XBlock","XSwitch") and t.col == col:
            if not any((ot.solid for ot in b.get_ts(t.x, t.y) if not ot is t)):
                xbs.append(t)
            else:
                error.play()
                return False
    for x in xbs:
        x.active = not x.active
    if xbs:
        switch.play()
        return True
def gswitch(b):
    gbs = []
    for t in b.itertiles():
        if t.name in ("GSwitch",):
            if not any((ot.solid for ot in b.get_ts(t.x, t.y) if not ot is t)):
                gbs.append(t)
            else:
                error.play()
                return False
    for g in gbs:
        g.active = not g.active
    if gbs:
        switch.play()
        return True
class XBlock(Tile):
    bimgs= Img.imgstripx("Tiles/XBlock")
    imgs=[[Img.multicolcopy(i, ((128,) * 3, col), ((64,) * 3, Img.darker(col)), ((160,) * 3, Img.lighter(col))) for i in bimgs] for col in cols]
    name="XBlock"
    def __init__(self,x,y,col,active=False):
        Tile.__init__(self,x,y)
        self.col=col
        self.active=active
    @property
    def img(self):
        return self.imgs[self.col][self.active]
    @property
    def solid(self):
        return self.active
    @property
    def state(self):
        return "XB"+str(self.col)+"A" if self.active else ""
class XSwitch(Tile):
    bimgs=[Img.imgrot(i) for i in Img.imgstripx("Tiles/XSwitch")]
    bimgs=bimgs[0]+bimgs[1]
    imgs=[[Img.multicolcopy(i, ((128,) * 3, col), ((64,) * 3, Img.darker(col))) for i in bimgs] for col in cols]
    name="XSwitch"
    def __init__(self,x,y,col,active=True,rot=2):
        Tile.__init__(self,x,y)
        self.col=col
        self.active=active
        self.r=rot
    def push(self,b):
        return xswitch(b,self.col)
    @property
    def img(self):
        return self.imgs[self.col][self.r+self.active*4]
    @property
    def solid(self):
        return self.active
    @property
    def pushdirs(self):
        return [D.dirs[self.r]]
class GSwitch(Tile):
    bimgs=[Img.imgrot(i) for i in Img.imgstripx("Tiles/GSwitch")]
    name="GSwitch"
    def __init__(self,x,y,rot=2,active=True):
        Tile.__init__(self,x,y)
        self.active=active
        self.r=rot
    def push(self,b):
        if gswitch(b):
            b.biome.gravity*=-1
            return True
    @property
    def img(self):
        return self.bimgs[self.active][self.r]
    @property
    def solid(self):
        return self.active
    @property
    def pushdirs(self):
        return [D.dirs[self.r]]
class XButton(Tile):
    imgs=[Img.colswap(Img.imgx("Tiles/XButton"), (64, 64, 64), c) for c in cols]
    interactive = True
    def __init__(self,x,y,c):
        Tile.__init__(self,x,y)
        self.col=c
    def interact(self,b,mb):
        return xswitch(b, self.col)
    @property
    def img(self):
        return self.imgs[self.col]
class Jelly(Block):
    interactive = 2
    goal = True
    valuable = True
    uts=[Img.UltraTiles("Jelly", Img.lighter(col, 0.3)) for col in cols]
    faces= Img.imgstripx("JellyFace")
    name="Jelly"
    sat=False
    updates = True
    spikable = True
    def __init__(self,x,y,gshape,col=0):
        Block.__init__(self, x, y, gshape)
        self.col = col
    def move(self,dx,dy,b):
        if dx and b.push(self.gshape,dx,dy):
            return True
        error.play()
        return False
    def satisfied(self,b):
        if self.sat:
            return True
        for g in b.goals:
            if g.name=="Jelly" and g.col==self.col and g not in self.gshape.tiles:
                return False
        self.sat=True
        return True
    def post_grav(self,b):
        stuck=False
        if not self.sat:
            for g in b.goals:
                if g.name=="Jelly" and g.col==self.col and g not in self.gshape.tiles and D.xydist((self.x,self.y),(g.x,g.y))==1:
                    self.gshape.tiles.append(g)
                    g.gshape=self.gshape
                    if not stuck:
                        stick.play()
                        stuck=True
        if stuck:
            b.re_img()
    def draw(self,b,screen):
        tpos=self.x*b.scale,self.y*b.scale
        screen.blit(self.img[b.iscale],tpos)
        screen.blit(self.faces[self.selected][b.iscale],tpos)
    @property
    def ut(self):
        return self.uts[self.col]
    @property
    def state(self):
        return "J"+str(self.col)+",".join((str(self.x),str(self.y)))
class Penguin(Tile):
    interactive = 2
    goal = True
    valuable = True
    portals = True
    imgs= Img.imgstripx("Penguin")
    name="Penguin"
    spikable = True
    d=0
    def __init__(self,x,y):
        Tile.__init__(self,x,y)
        self.gshape=GravShape(self)
    def move(self,dx,dy,b):
        if dx:
            self.d=dx
            for t in b.get_ts(self.x+dx,self.y):
                if t.solid and (dx,0) in t.pushdirs:
                    if t.push(b):
                        b.move(self,dx,dy)
                        return True
                    else:
                        error.play()
                        return False
            if b.push(self.gshape,dx,dy):
                return True
        error.play()
        return False
    @property
    def state(self):
        return "Peng"+",".join((str(self.x),str(self.y)))
    @property
    def img(self):
        return self.imgs[(self.d==-1)+self.selected*2]
class Thud(Tile):
    interactive = 2
    goal = True
    valuable = True
    portals = True
    imgs= Img.imgstripx("Thud")
    name="Thud"
    grav=0
    def __init__(self,x,y):
        Tile.__init__(self,x,y)
        self.gshape=GravShape(self)
    def move(self,dx,dy,b):
        moved=False
        while b.exists(self) and b.push(self.gshape,dx,dy,fail_deadly=True):
            b.goal_test()
            moved=True
        for t in b.get_ts(self.x+dx,self.y+dy):
            if t.solid and (dx,dy) in t.pushdirs:
                if t.push(b):
                    b.move(self,dx,dy)
                    moved=True
                else:
                    error.play()
                    return False
        if moved:
            thud.play()
            return True
        else:
            error.play()
            return False
    @property
    def state(self):
        return self.name+",".join((str(self.x),str(self.y)))
    @property
    def img(self):
        return self.imgs[self.selected]
class SpikyThud(Thud):
    imgs = Img.imgstripx("SpikyThud")
    name = "SpikyThud"
    spiky = True
class BlockExtension(Tile):
    eimg=None
    def __init__(self,block):
        self.block=block
        self.shape=block.gshape
class Mover(BlockExtension):
    interactive = 2
    imgs= Img.imgstripx("Blocks/Mover")
    eimg=imgs[1]
    def move(self,dx,dy,b):
        if b.push(self.shape,dx,dy):
            return True
        else:
            error.play()
    @property
    def img(self):
        return self.imgs[self.block.selected]

