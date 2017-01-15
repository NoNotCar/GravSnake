from Tiles import Tile,GravShape
from Img import imgstripx,tilemapx, multicolcopy,sndget,ImageManager
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
    def __init__(self,h,t,col_function=gen_col):
        ImageManager.__init__(self)
        self.h=h
        self.t=t
        self.cf=col_function
    def gen_img(self):
        col = self.cf()
        return ([multicolcopy(i, ((128, 128, 128), col), ((64, 64, 64), tuple(c // 2 for c in col))) for i in self.h],
                                   [multicolcopy(i, ((128, 128, 128), col),((64, 64, 64), tuple(c // 2 for c in col))) for i in self.t])
IM_SNAKE=SnakeImageManager(imgstripx("SnakeHead"),tilemapx("SnakeSeg"))
IM_ANTISNAKE=SnakeImageManager(imgstripx("AntiHead"),tilemapx("SnakeSeg"))
IM_IRONSNAKE=SnakeImageManager(imgstripx("IronSnakeHead"),tilemapx("IronSnakeSeg"),lambda:tuple(randint(100, 150) for _ in range(3)))
class SnakeSeg(Tile):
    name="SnakeSeg"
    spikable = True
    dconv={1:0,2:1,4:2,8:3}
    def __init__(self,x,y,bdir,fdir,snake):
        Tile.__init__(self, x, y)
        self.bdir,self.fdir=bdir,fdir
        self.snake=snake
        snake.tiles.append(self)
        self.gshape=snake
    def is_face(self,dx,dy):
        return (dx,dy) not in [D.dirs[self.dconv[d]] for d in (self.fdir,self.bdir) if d]
    @property
    def img(self):
        return self.snake.tailimgs[self.fdir+self.bdir]
class IronSnakeSeg(SnakeSeg):
    spikable = False
class AntiSnakeSeg(SnakeSeg):
    grav = -1
class SnakeHead(Tile):
    name="SnakeHead"
    selected=True
    spikable = True
    segclass=SnakeSeg
    eimg = imgstripx("SnakeHead")[3]
    def __init__(self,x,y,snake):
        Tile.__init__(self,x,y)
        self.snake=snake
        tx,ty=snake.tiles[-1].x,snake.tiles[-1].y
        snake.tiles.append(self)
        self.d=D.dirs.index((x-tx,y-ty))
        self.gshape=snake
    def move(self,b,dx,dy):
        tx,ty=self.x+dx,self.y+dy
        snake=self.snake.tiles
        eating=False
        if b.in_world(tx,ty):
            for t in b.get_ts(tx,ty):
                if t.edible:
                    eating=t.eat(b)
                    b.dest(t)
                    t.on_dest(b)
                    b.re_img()
                    if not b.turbo:
                        grow.play()
                    break
                elif t.gshape and t not in snake and not (t.spiky and self.spikable):
                    if b.snake_push(t.gshape,dx,dy,self.snake):
                        break
                    else:
                        nomove.play()
                        return False
                elif t.is_face(-dx,-dy) or t in snake:
                    if not b.turbo:
                        nomove.play()
                    return False
        else:
            return False
        if not eating:
            b.dest(snake.pop(0))
            snake[0].bdir = 0
        nd=D.dirs.index((dx, dy))
        snake.remove(self)
        s=self.segclass(self.x,self.y,2**((self.d+2)%4) if len(snake) else 0,2**nd,self.snake)
        snake.append(self)
        b.spawn(s)
        b.move(self,dx,dy)
        self.d=nd
        return True
    def is_face(self,dx,dy):
        return (dx,dy) != D.dirs[(self.d+2)%4]
    @property
    def img(self):
        return self.snake.headimgs[(self.d+2)%4+4*self.selected]
    @property
    def state(self):
        return ",".join(s.name+str((s.x,s.y)) for s in self.snake.tiles)
class IronSnakeHead(SnakeHead):
    spikable = False
    segclass = IronSnakeSeg
    eimg=imgstripx("IronSnakeHead")[3]
class AntiSnakeHead(SnakeHead):
    segclass = AntiSnakeSeg
    grav = -1
    eimg = imgstripx("AntiHead")[3]
class Snake(GravShape):
    head=SnakeHead
    im=IM_SNAKE
    def __init__(self,*tiles):
        GravShape.__init__(self,*tiles)
        self.iid=self.im.register()
    @property
    def tailimgs(self):
        return self.im[self.iid][1]
    @property
    def headimgs(self):
        return self.im[self.iid][0]
class IronSnake(Snake):
    head = IronSnakeHead
    im=IM_IRONSNAKE
class AntiSnake(Snake):
    head = AntiSnakeHead
    im=IM_ANTISNAKE


