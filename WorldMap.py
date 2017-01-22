import WMObjects
import Img
import Direction as D
import pygame
mm=Img.imgx("MapMan")
MOVEMENT=0
UNLOCK=1
COMPLETE=2
lcomplete=Img.sndget("lcomplete")
reveal=Img.sndget("beep")
kconv={pygame.K_w:(0,-1),pygame.K_a:(-1,0),pygame.K_s:(0,1),pygame.K_d:(1,0),
       pygame.K_UP: (0, -1), pygame.K_LEFT: (-1, 0), pygame.K_DOWN: (0, 1), pygame.K_RIGHT: (1, 0)}
class RunLevel(Exception):
    def __init__(self,b):
        self.b=b
class WorldMap(object):
    iscale = 3
    rscale = 64
    back=(0,148,255)
    game=False
    px,py=0,0
    state=UNLOCK
    up=0
    speed=5
    acool=speed
    def __init__(self, size, scale=64):
        self.sx, self.sy = size
        self.paths = [[None for y in range(self.sy)] for x in range(self.sx)]
        self.terrain=[[None for y in range(self.sy)] for x in range(self.sx)]
        self.re_img()
        self.scale = scale
        self.unodes=[]
    def render(self, screen):
        screen.fill(self.back)
        for x,y in self.iterlocs():
            t=self.get_t(x,y)
            if t:
                screen.blit(t.img[self.iscale],(x*self.scale,y*self.scale))
        for p,x,y in self.iterpaths(True):
            p.draw(x,y,screen,self)
        if self.game:
            screen.blit(mm[self.iscale],(self.px*self.scale,self.py*self.scale))
    def update(self, events, mx, my):
        if self.state:
            if self.acool:
                self.acool-=1
            else:
                self.acool=self.speed
                if self.state==UNLOCK:
                    self.unlock()
                    if self.state==UNLOCK:
                        reveal.play()
                elif self.state==COMPLETE:
                    lcomplete.play()
                    p=self.get_p(self.px,self.py)
                    p.progress=1
                    self.unodes=[(self.px,self.py)]
                    self.state=UNLOCK
                    self.unlock(True)
        else:
            for e in events:
                if  e.type == pygame.KEYDOWN:
                    if e.key in kconv.keys():
                        kx, ky = kconv[e.key]
                        tx,ty=self.px+kx,self.py+ky
                        p=self.get_p(tx,ty)
                        if p and p.revealed:
                            self.px,self.py=tx,ty
                    elif e.key==pygame.K_SPACE:
                        p=self.get_p(self.px,self.py)
                        if p and p.name=="Level":
                            if not p.progress:
                                self.state=COMPLETE
                            raise RunLevel(p.b)
    def iterlocs(self):
        for x in range(self.sx):
            for y in range(self.sy):
                yield x, y

    def iterpaths(self, pos=False):
        if pos:
            for x, y in self.iterlocs():
                p=self.get_p(x, y)
                if p:
                    yield p,x,y
        else:
            for x, y in self.iterlocs():
                p = self.get_p(x, y)
                if p:
                    yield p
    def iterterrs(self, pos=False):
        if pos:
            for x, y in self.iterlocs():
                t=self.get_t(x, y)
                if t:
                    yield t,x,y
        else:
            for x, y in self.iterlocs():
                t = self.get_t(x, y)
                if t:
                    yield t

    def in_world(self, x, y):
        return 0 <= x < self.sx and 0 <= y < self.sy

    def get_p(self, x, y):
        if self.in_world(x, y):
            return self.paths[x][y]
    def get_t(self, x, y):
        if self.in_world(x, y):
            return self.terrain[x][y]

    def spawn(self, p):
        self.paths[p.x][p.y]=p

    def dest(self, p):
        self.paths[p.x][p.y]=p

    def resize(self, h, big):
        for array in self.paths,self.terrain:
            if h and big:
                array.append([None for _ in range(self.sy)])
            elif big:
                for x, c in enumerate(array):
                    c.append(None)
            elif h:
                array.pop()
            else:
                for c in array:
                    c.pop()
        if h:
            self.sx += 1 if big else -1
        else:
            self.sy += 1 if big else -1

    def re_img(self):
        for t,x,y in self.iterterrs(True):
            t.re_img(self,x,y)
        for p,x,y in self.iterpaths(True):
            p.re_img(self,x,y)

    def prepare(self):
        for p,x,y in self.iterpaths(True):
            p.revealed=False
        for p, x, y in self.iterpaths(True):
            if p.__class__==WMObjects.Spawn:
                self.px, self.py =x,y
                self.unodes.append((x,y))
        self.re_img()
        self.game=True
    def unlock(self,force=False):
        try:
            nx,ny=self.unodes[self.up]
        except IndexError:
            self.state=MOVEMENT
            self.unodes=[]
            self.up=0
            return None
        p=self.get_p(nx,ny)
        if p and (not p.revealed or force):
            p.revealed=True
            if p.progress:
                self.unodes.extend(p for p in D.iter_offsets(nx,ny) if p not in self.unodes)
        self.up+=1
        self.re_img()
    def cancel(self):
        self.state=MOVEMENT
    @property
    def scale(self):
        return self.rscale

    @scale.setter
    def scale(self, n):
        self.rscale = n
        self.iscale = self.scale // 16 - 1
        self.ascale = self.scale // 16

