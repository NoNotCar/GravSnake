from Tiles import Tile,Block
import Img
import Direction as D
switch=Img.sndget("switch")
error=Img.sndget("nomove")
stick=Img.sndget("stick")
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
class XBlock(Tile):
    bimgs=Img.imgstripx("Tiles/XBlock")
    imgs=[[Img.multicolcopy(i,((128,)*3,col),((64,)*3,Img.darker(col)),((160,)*3,Img.lighter(col))) for i in bimgs] for col in cols]
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
    imgs=[[Img.multicolcopy(i,((128,)*3,col),((64,)*3,Img.darker(col))) for i in bimgs] for col in cols]
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
class XButton(Tile):
    imgs=[Img.colswap(Img.imgx("Tiles/XButton"),(64,64,64),c) for c in cols]
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
    uts=[Img.UltraTiles("Jelly",Img.lighter(col,0.3)) for col in cols]
    faces=Img.imgstripx("JellyFace")
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
        if not self.sat:
            for g in b.goals:
                if g.name=="Jelly" and g.col==self.col and g not in self.gshape.tiles and D.xydist((self.x,self.y),(g.x,g.y))==1:
                    self.gshape.tiles.append(g)
                    g.gshape=self.gshape
                    stick.play()
                    self.re_img(b)
                    g.re_img(b)
    def draw(self,b,screen):
        tpos=self.x*b.scale,self.y*b.scale
        screen.blit(self.img[b.iscale],tpos)
        screen.blit(self.faces[self.selected][b.iscale],tpos)
    @property
    def ut(self):
        return self.uts[self.col]


