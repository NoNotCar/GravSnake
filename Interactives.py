from Tiles import Tile
import Img
switch=Img.sndget("switch")
error=Img.sndget("nomove")
cols=[(255,0,0),(0,0,255),(255,255,0),(0,255,0)]
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
        return "XB"+"A" if self.active else ""
class XButton(Tile):
    imgs=[Img.colswap(Img.imgx("Tiles/XButton"),(64,64,64),c) for c in cols]
    interactive = True
    def __init__(self,x,y,c):
        Tile.__init__(self,x,y)
        self.col=c
    def interact(self,b,mb):
        xbs=[]
        for t in b.itertiles():
            if t.name=="XBlock" and t.col==self.col:
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
    @property
    def img(self):
        return self.imgs[self.col]