from Tiles import Tile,GravShape
from Img import imgstripx,tilemapx, multicolcopy,sndget,ImageManager,NSUltraTiles
from random import randint
import Direction as D
from copy import deepcopy
nomove=sndget("nomove")
grow=sndget("grow")
def gen_col():
    while True:
        snakecol=tuple(randint(0,255) for _ in range(3))
        if any(c>128 for c in snakecol):
            return snakecol
class SnakeImageManager(ImageManager):
    def __init__(self,t,col_function=gen_col):
        ImageManager.__init__(self)
        self.t=t
        self.cf=col_function
    def gen_img(self):
        col = self.cf()
        return NSUltraTiles(self.t,col,((64, 64, 64), tuple(c // 2 for c in col)))
IM_SNAKE=SnakeImageManager("SnakeSeg")
IM_IRONSNAKE=SnakeImageManager("IronSnakeSeg",lambda:tuple(randint(100, 150) for _ in range(3)))
class SnakeSeg(Tile):
    name="SnakeSeg"
    spikable = True
    dconv={1:0,2:1,4:2,8:3}
    valuable = True
    i=(0,0,0,0)
    def __init__(self,x,y,bdir,fdir,snake):
        Tile.__init__(self, x, y)
        self.bdir,self.fdir=bdir,fdir
        self.snake=snake
        snake.tiles.append(self)
        self.gshape=snake
    def is_face(self,dx,dy):
        return (dx,dy) not in [D.dirs[d] for d in (self.fdir,self.bdir) if d]
    def on_dest(self,b):
        if b.game:
            raise RuntimeError,"SNEK DELETED IN GAME"
        else:
            for s in self.snake.tiles:
                if not s is self:
                    b.dest(s)
    def re_img(self,b,lstart=True):
        self.i=tuple(n in (self.bdir,self.fdir) for n in range(4))
    @property
    def img(self):
        return self.snake.tailimgs[self.i]
    @property
    def grav(self):
        return self.snake.grav
class IronSnakeSeg(SnakeSeg):
    spikable = False
class SnakeHead(Tile):
    name="SnakeHead"
    spikable = True
    segclass=SnakeSeg
    valuable = True
    goal=True
    portals = True
    zipped=False
    eimg = imgstripx("SnakeHead")[3]
    faces={-1:imgstripx("AntiSnakeFace")+imgstripx("ZippedAntiSnakeFace"),1:imgstripx("SnakeFace")+imgstripx("ZippedSnakeFace")}
    interactive = 2
    def __init__(self,x,y,snake):
        Tile.__init__(self,x,y)
        self.snake=snake
        tx,ty=snake.tiles[-1].x,snake.tiles[-1].y
        snake.tiles.append(self)
        self.d=D.dirs.index((x-tx,y-ty))
        self.gshape=snake
    def move(self,dx,dy,b):
        tx,ty=self.x+dx,self.y+dy
        snake=self.snake.tiles
        for s in snake:
            if s.name != "SnakeHead" and s.bdir is None:
                tail=s
                break
        else:
            raise RuntimeError, "NO TAIL DETECTED"
        eating=False
        if b.in_world(tx,ty):
            for t in b.get_ts(tx,ty):
                if t.edible and not self.zipped:
                    eating= t.eat(b, self)
                    b.dest(t)
                    t.on_dest(b)
                    b.re_img()
                    grow.play()
                    break
                elif t.gshape and t not in snake and not (t.spiky and self.spikable):
                    if b.push(t.gshape, dx, dy, self.snake,tail):
                        break
                    else:
                        nomove.play()
                        return False
                elif t.solid and (dx,dy) in t.pushdirs:
                    if not t.push(b):
                        return False
                elif t.is_face(-dx,-dy) or t in snake:
                    nomove.play()
                    return False
        else:
            return False
        if not eating:
            snake.remove(tail)
            b.dest(tail)
            spos=set((t.x,t.y) for t in snake)
            for s in snake:
                if s.name!="SnakeHead" and D.add_vs((s.x,s.y),D.get_dir(s.bdir)) not in spos:
                    s.bdir=None
                    s.re_img(b)
                    break
        nd=D.dirs.index((dx, dy))
        s=self.segclass(self.x,self.y,(self.d+2)%4 if len(snake)>1 else None,nd,self.snake)
        s.re_img(b)
        b.spawn(s)
        b.move(self,dx,dy)
        self.d=nd
        return True
    def is_face(self,dx,dy):
        return (dx,dy) != D.get_dir(self.d+2)
    def draw(self,b,screen):
        tpos=self.x*b.scale,self.y*b.scale
        screen.blit(self.img[b.iscale],tpos)
        screen.blit(self.faces[self.grav][self.selected+self.zipped*2][b.iscale],tpos)
    def on_dest(self,b):
        if b.game:
            raise RuntimeError,"SNEK DELETED IN GAME"
        else:
            for s in self.snake.tiles:
                if not s is self:
                    b.dest(s)
    @property
    def img(self):
        return self.snake.tailimgs[tuple(n==((self.d+2)%4) for n in xrange(4))]
    @property
    def state(self):
        return ",".join(s.name+str((s.x,s.y)) for s in self.snake.tiles)
    @property
    def grav(self):
        return self.snake.grav
class IronSnakeHead(SnakeHead):
    spikable = False
    segclass = IronSnakeSeg
    eimg=imgstripx("IronSnakeHead")[3]
class Snake(GravShape):
    head=SnakeHead
    im=IM_SNAKE
    grav=1
    def __init__(self,*tiles):
        GravShape.__init__(self,*tiles)
        self.iid=self.im.register()
    @property
    def tailimgs(self):
        return self.im[self.iid]
    @property
    def headimgs(self):
        return self.im[self.iid]
class IronSnake(Snake):
    head = IronSnakeHead
    im=IM_IRONSNAKE


