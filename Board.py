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
kconv={pygame.K_w:(0,-1),pygame.K_a:(-1,0),pygame.K_s:(0,1),pygame.K_d:(1,0),
       pygame.K_UP: (0, -1), pygame.K_LEFT: (-1, 0), pygame.K_DOWN: (0, 1), pygame.K_RIGHT: (1, 0)}
portal=Img.sndget("portal")
exp=Img.sndget("exp")
speed=5
musics=["Overworld","Mars"]
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
    biome=Biomes.Islands
    controlled=None
    music="Overworld"
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
                        self.goal_test()
                    else:
                        self.phase=INPUT
                        [t.post_grav(self) for t in self.updatables]
                        self.goal_test()
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
                    for t in self.get_ts(mx,my):
                        if t.interactive:
                            if t.interactive==2:
                                if self.controlled:
                                    self.controlled.selected=False
                                self.controlled=t
                                self.controlled.selected=True
                            elif t.interact(self,e.button):
                                self.tcool = speed
                                self.phase = GRAVITY
                                [t.pre_grav(self) for t in self.updatables]
                                self.goal_test()
                                break
                if self.controlled and e.type==pygame.KEYDOWN:
                    if e.key in kconv.keys():
                        kx,ky=kconv[e.key]
                        if self.controlled.move(kx,ky,self):
                            self.tcool=speed
                            self.phase=GRAVITY
                            [t.pre_grav(self) for t in self.updatables]
                            self.goal_test()
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
    def push(self, pshape, dx, dy, snake=None):
        cgroup = pshape.tiles[:]
        spiked=set()
        spiking=set()
        ok=set()
        for c,cx, cy in ((c,c.x, c.y) for c in cgroup if c.is_face(dx,dy)):
            if not self.in_world(cx+dx, cy+dy):
                break
            for ot in self.get_ts(cx+dx, cy+dy):
                if ot in cgroup or snake and ot is snake.tiles[0]:
                    continue
                elif snake and ot in snake.tiles:
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
            if o.valuable:
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
        for ts in itertools.chain(*self.t):
            for t in ts:
                t.re_img(self)
    def goal_test(self):
        if not self.fruit:
            for g in self.goals[:]:
                if g.portals and any(t for t in self.get_ts(g.x,g.y) if t.name=="Portal"):
                    self.goals.remove(g)
                    for s in g.gshape.tiles:
                        self.dest(s)
                        if s is self.controlled:
                            self.controlled=None
                    portal.play()
        if all(g.satisfied(self) for g in self.goals):
            raise GameEnd(False,"WIN")
    def prepare(self):
        self.goals=[]
        self.updatables=[]
        self.game=True
        for t in self.itertiles():
            if t.interactive==2 and not self.controlled:
                self.controlled=t
            elif t.name=="Fruit":
                self.fruit+=1
            if t.goal:
                self.goals.append(t)
            if t.updates:
                self.updatables.append(t)
        if self.controlled:
            self.controlled.selected=True
        self.re_img()
        self.lstate=self.state
        self.biome=self.biome()
        Img.musplay(self.music)
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



