import Img
from Tiles import Tile,SBlockTile
move=Img.sndget("cpmove")
class CSelector(Tile):
    solid = False
    img=Img.imgx("Select")
    interactive = 1
    def __init__(self,x,y,p):
        Tile.__init__(self,x,y)
        self.p=p
    def interact(self,b,mb):
        b.move(self.p,self.x-self.p.x,self.y-self.p.y)
        move.play()
        return True
class ChessPiece(SBlockTile):
    interactive = 2
    valuable = 1
    goal = 1
    portals = 1
    updates = 1
    spikable = True
    def __init__(self,x,y):
        SBlockTile.__init__(self,x,y)
        self.selectors=[]
    def gen_selpos(self,b):
        return []
    def gen_sels(self,b):
        for x,y in self.gen_selpos(b):
            cs=CSelector(x,y,self)
            b.spawn(cs)
            self.selectors.append(cs)
    def valid(self,x,y,b):
        return b.in_world(x,y) and not any(t.solid for t in b.get_ts(x,y))
    def dest_sels(self,b):
        while self.selectors:
            b.dest(self.selectors.pop())
    def on_select(self,b):
        self.gen_sels(b)
    def post_grav(self,b):
        if self.selected:
            self.gen_sels(b)
    def pre_grav(self,b):
        self.dest_sels(b)
    def on_deselect(self,b):
        self.dest_sels(b)
    @property
    def state(self):
        return self.__class__.__name__+str((self.x,self.y))
class Knight(ChessPiece):
    img=Img.imgx("Chess/Knight")
    def gen_selpos(self,b):
        for dx,dy in [(-1,-2),(1,-2),(-1,2),(1,2),(-2,-1),(-2,1),(2,-1),(2,1)]:
            if self.valid(self.x+dx,self.y+dy,b):
                yield self.x+dx,self.y+dy
class Bishop(ChessPiece):
    img=Img.imgx("Chess/Bishop")
    def gen_selpos(self,b):
        for dx,dy in ((-1,-1),(-1,1),(1,-1),(1,1)):
            n=1
            while True:
                tx,ty=self.x+dx*n,self.y+dy*n
                if self.valid(tx,ty,b):
                    yield tx,ty
                    n+=1
                    continue
                break
