import Img
from random import choice, randint
import pygame
import itertools
import Direction as D
import Tiles
import Biomes
from collections import deque
from copy import deepcopy
white=(255,255,255)
INPUT=0
GRAVITY=1
EXPLODING=2
class GameEnd(Exception):
    def __init__(self,fail,code):
        self.fail=fail
        self.code=code
class ImpossibleException(Exception):
    pass
class Solution(Exception):
    def __init__(self,solution):
        self.solution=solution
kconv={pygame.K_w:(0,-1),pygame.K_a:(-1,0),pygame.K_s:(0,1),pygame.K_d:(1,0)}
portal=Img.sndget("portal")
exp=Img.sndget("exp")
speed=5
class Board(object):
    tcool=0
    game=False
    nodes=None
    iscale=3
    zones=2
    lspawn=None
    rscale=64
    phase=GRAVITY
    fruit=0
    turbo=False
    biome=Biomes.Islands
    def __init__(self,size,scale=64):
        self.sx,self.sy=size
        self.t=[[[Tiles.Air(x,y)] for y in range(self.sy)] for x in range(self.sx)]
        self.re_img()
        self.scale=scale
    def render(self,screen):
        if self.game:
            self.biome.render_back(screen,self)
        for t in self.itertiles():
            t.draw(self,screen)
        if self.game:
            self.biome.render_front(screen,self)
    def update(self,events,mx,my):
        if self.phase:
            if self.tcool:
                self.tcool-=1
            else:
                if self.phase==GRAVITY:
                    if self.grav():
                        self.tcool=speed*(1 if self.phase==GRAVITY else 4)
                        self.snake_goal_test()
                    else:
                        self.phase=INPUT
                        self.snake_goal_test()
                        state=self.state
                        if state!=self.lstate:
                            self.lstate=state
                            return deepcopy(self)
                elif self.phase==EXPLODING:
                    for t in self.itertiles():
                        if t.name=="Exp":
                            self.dest(t)
                    self.phase=GRAVITY
        else:
            for e in events:
                if e.type==pygame.MOUSEBUTTONDOWN:
                    nsh=[sh for sh in self.shs if (sh.x,sh.y)==(mx,my)]
                    if nsh:
                        self.shead.selected=False
                        self.shead=nsh[0]
                        self.shead.selected = True
                        break
                if e.type==pygame.KEYDOWN:
                    if e.key in kconv.keys():
                        if self.shead.move(self,*kconv[e.key]):
                            self.tcool=speed
                            self.phase=GRAVITY
                            self.snake_goal_test()
                            break
                    elif e.key==pygame.K_r:
                        raise GameEnd(True,"RESET")
    def iterlocs(self):
        for x in range(self.sx):
            for y in range(self.sy):
                yield x,y
    def itertiles(self,pos=False):
        if pos:
            for x,y in self.iterlocs():
                for t in self.get_ts(x,y):
                    yield x,y,t
        else:
            for x,y in self.iterlocs():
                for t in self.get_ts(x,y):
                    yield t
    def grav(self):
        grav=False
        fixed=set()
        shapes=[t.gshape for t in self.itertiles() if t.gshape and t.grav]
        for s in sorted(shapes,key=lambda s:s.tiles[0].grav,reverse=True):
            if s.tiles[0] in fixed:
                continue
            cgroup=s.tiles[:]
            ocgroup=cgroup[:]
            failnofall=None
            g=s.tiles[0].grav
            for c,cx,cy in ((c,c.x,c.y) for c in cgroup if c.is_face(0,g)):
                for ot in self.get_ts(cx,cy+g):
                    if c in ocgroup:
                        if failnofall is None and any((c.spiky and ot.spikable,c.spikable and ot.spiky)):
                            failnofall=True
                        elif not (failnofall is False) and ot.is_face(0,-g) and not any((c.spiky and ot.spikable,c.spikable and ot.spiky)):
                            failnofall=False
                    if ot in cgroup:
                        continue
                    elif ot in fixed and not failnofall:
                        fixed.update(ocgroup)
                        break
                    elif ot.gshape and ot.grav==g:
                        cgroup.extend(ot.gshape.tiles)
                        continue
                    elif ot.is_face(0,-g) and not failnofall:
                        fixed.update(ocgroup)
                        break
                else:
                    continue
                break
            else:
                exps=set()
                for ct in cgroup:
                    e=self.move(ct,0,g)
                    if e:
                        exps|=set(e.gshape.tiles)
                for e in exps:
                    if self.in_world(e.x,e.y):
                        self.dest(e)
                        self.spawn(Tiles.Explosion(e.x,e.y))
                        self.phase=EXPLODING
                fixed.update(cgroup)
                grav=True
            if failnofall:
                raise GameEnd(True, "FAIL")
        if self.phase==EXPLODING:
            exp.play()
        return grav
    def snake_push(self,pshape,dx,dy,snake):
        cgroup = pshape.tiles[:]
        spiked=set()
        spiking=set()
        ok=set()
        for c,cx, cy in ((c,c.x, c.y) for c in cgroup if c.is_face(dx,dy)):
            if not self.in_world(cx+dx, cy+dy):
                break
            for ot in self.get_ts(cx+dx, cy+dy):
                if ot in cgroup or ot is snake.tiles[0]:
                    continue
                elif ot in snake.tiles:
                    break
                elif ot.gshape:
                    if ot.spiky and c.spikable:
                        if ot.gshape not in spiking|ok:
                            spiking.add(ot.gshape)
                    elif c.spiky and ot.spikable:
                        if ot.gshape not in spiked|ok:
                            spiked.add(ot.gshape)
                    else:
                        for spset in spiked,spiking:
                            if ot.gshape in spset:
                                spset.remove(ot.gshape)
                                ok.add(ot.gshape)
                                cgroup.extend(ot.gshape.tiles)
                                break
                        else:
                            cgroup.extend(ot.gshape.tiles)
                    continue
                elif ot.is_face(-dx,-dy):
                    break
            else:
                continue
            break
        else:
            if not any((spiking,spiked)):
                for ct in cgroup:
                    self.move(ct, dx, dy)
                return True
        return False
    def execute_move(self,move):
        snum,(dx,dy)=move
        self.shs[snum].move(self, dx,dy)
        if self.turbo:
            self.history.append(((snum,(dx,dy)),self.state))
        self.snake_goal_test()
        while self.grav():
            self.snake_goal_test()
    def in_world(self,x,y):
        return 0<=x<self.sx and 0<=y<self.sy
    def get_ts(self,x,y):
        if self.in_world(x,y):
            for t in self.t[x][y]:
                yield t
    def spawn(self,s):
        self.t[s.x][s.y].append(s)
    def dest(self,s):
        self.t[s.x][s.y].remove(s)
    def move(self,o,dx,dy):
        self.dest(o)
        o.x+=dx
        o.y+=dy
        if o.y>=self.sy or o.y<0:
            if "Snake" in o.name:
                raise GameEnd(True, "FAIL")
            return o
        else:
            self.spawn(o)
    def resize(self,h,big):
        for array in self.t,:
            if h and big:
                array.append([[Tiles.Air(self.sx,y)] for y in range(self.sy)])
            elif big:
                for x,c in enumerate(array):
                    c.append([Tiles.Air(x,self.sy)])
            elif h:
                array.pop()
            else:
                for c in array:
                    c.pop()
        if h:
            self.sx +=1 if big else -1
        else:
            self.sy += 1 if big else -1
    def re_img(self):
        if self.turbo:
            return None
        for ts in itertools.chain(*self.t):
            for t in ts:
                t.re_img(self)
    def snake_goal_test(self):
        if not self.fruit:
            for sh in self.shs:
                if any(t for t in self.get_ts(sh.x,sh.y) if t.name=="Portal"):
                    for s in sh.snake.tiles:
                        self.dest(s)
                    self.shs.remove(sh)
                    if not self.turbo:
                        portal.play()
                    if not self.shs:
                        raise GameEnd(False,"WIN")
    def prepare(self,game=True):
        self.shs=[]
        self.game=game
        for t in self.itertiles():
            if t.name=="SnakeHead":
                self.shs.append(t)
                t.selected=False
            elif t.name=="Fruit":
                self.fruit+=1
        self.shead=self.shs[0]
        self.shead.selected=True
        if game:
            self.re_img()
            self.lstate=self.state
            self.biome=self.biome()
        else:
            self.turbo=True
            self.history=[]
    @property
    def scale(self):
        return self.rscale
    @scale.setter
    def scale(self,n):
        self.rscale=n
        self.iscale=self.scale//16-1
        self.ascale=self.scale//16
    @property
    def state(self):
        return ";".join(t.state for t in self.itertiles() if t.state)
class Solver(object):
    def __init__(self,board):
        board.prepare(False)
        self.states=deque([board])
        self.past_states={board.state}
        self.best_solution=None
    def update(self):
        if self.states:
            cb=self.states.popleft()
            for move in itertools.product(xrange(len(cb.shs)),D.dirs):
                nb=deepcopy(cb)
                try:
                    nb.execute_move(move)
                except GameEnd as ge:
                    if not ge.fail:
                        raise Solution([m for m,s in nb.history])
                    else:
                        continue
                if nb.state not in self.past_states:
                    self.states.appendleft(nb)
                    self.past_states.add(nb.state)
        else:
            raise ImpossibleException



