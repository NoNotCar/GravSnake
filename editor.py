import pygame, sys
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(pygame.display.list_modes()[0],pygame.FULLSCREEN)
clock=pygame.time.Clock()
import Board, Img
import EditorButtons as B
import pickle
import Tiles
import Interactives
import Direction as D
from Snake import Snake,IronSnake
from random import choice
from copy import deepcopy
from LevelRunner import run
size=(12,12)
scale=64
b=Board.Board(size)
def resize_ss():
    global ss,r,scale
    scale=b.scale
    r = pygame.Rect(0, 0, b.sx * scale, b.sy * scale)
    r.center = screen.get_rect().center
    ss = screen.subsurface(r)
resize_ss()
downscale={64:48,48:32,32:16,16:16}
buttons=[B.ExternalButton("New"),B.Resizer(0),B.Resizer(1),B.Scaler(),B.ExternalButton("Play")]
placers=[B.Rotator(),B.TerrainPlacer(Tiles.Dirt),B.TerrainPlacer(Tiles.Snow),B.TerrainPlacer(Tiles.WoodPlatform),B.TerrainPlacer(Tiles.Portal),
         B.SnakePlacer(Snake),B.SnakePlacer(IronSnake),B.TerrainPlacer(Tiles.Fruit),B.TerrainPlacer(Tiles.Spikes),
         B.BlockPlacer(),B.CloudBlockPlacer(),B.SpikeBlockPlacer(),
         B.NTerrainPlacer(Interactives.XBlock,4,0),B.NTerrainPlacer(Interactives.XBlock,4,1),
         B.NTerrainPlacer(Interactives.XSwitch,4),B.NTerrainPlacer(Interactives.XSwitch,4,0),B.NTerrainPlacer(Interactives.XButton,4),
         B.TerrainPlacer(Tiles.Diamond),B.JellyPlacer(),B.TerrainPlacer(Interactives.Penguin)]
br=pygame.Rect(0,0,len(buttons)*64,64)
br.centerx=screen.get_rect().centerx
bss=screen.subsurface(br)
pr=pygame.Rect(0,0,(len(placers)-1)//16*64+64,min(len(placers)*64,1024))
pr.centery=screen.get_rect().centery
pss=screen.subsurface(pr)
selected=0
selimg=Img.imgx("Select")
screen.fill((100,100,100))
pygame.display.flip()
saving=False
savename="Levels/test"
multipos=[]
error=Img.sndget("nomove")
def check_exit(event):
    if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
            sys.exit()
while True:
    flip=False
    es=pygame.event.get()
    mx,my=pygame.mouse.get_pos()
    for e in es:
        if e.type==pygame.MOUSEBUTTONDOWN:
            if e.button in [4,5]:
                placers[selected].scroll(-1 if e.button==4 else 1)
            elif br.collidepoint(mx,my):
                try:
                    if buttons[(mx-br.left)//64].on_click(e.button,b):
                        while True:
                            try:
                                resize_ss()
                                break
                            except ValueError:
                                scale = downscale[scale]
                                b.scale = scale
                        screen.fill((100, 100, 100))
                        flip=True
                except B.ExternalMethod as m:
                    if m.task=="Play":
                        pb=deepcopy(b)
                        try:
                            pb.prepare()
                        except RuntimeError:
                            del pb
                            error.play()
                            continue
                        run(pb,screen,ss,r)
                        pygame.mixer.music.stop()
                    elif m.task=="New":
                        b=Board.Board((b.sx,b.sy),b.scale)
                        for im in Img.imss:
                            im.reload()
                    flip=True
            elif pr.collidepoint(mx,my):
                nsel=(my-pr.top)//64+mx//64*16
                selected=nsel if nsel<len(placers) else selected
        elif e.type==pygame.KEYDOWN:
            kmods=pygame.key.get_mods()
            if e.key==pygame.K_s and kmods&pygame.KMOD_CTRL:
                if saving=="save":
                    with open(Img.np(Img.loc + savename+".lvl"), "w") as save:
                        pickle.dump(b, save)
                    saving=False
                elif saving:
                    saving=False
                else:
                    saving="save"
            elif e.key==pygame.K_o and kmods&pygame.KMOD_CTRL:
                if saving=="open":
                    try:
                        with open(Img.np(Img.loc + savename+".lvl"), "r") as save:
                            b=pickle.load(save)
                            resize_ss()
                    except IOError:
                        pass
                    saving=False
                    flip=True
                elif saving:
                    saving=False
                else:
                    saving="open"
            elif saving:
                if e.key==pygame.K_BACKSPACE and len(savename):
                    savename=savename[:-1]
                else:
                    u=e.unicode
                    savename+=u.upper() if kmods&pygame.KMOD_LSHIFT else u
                flip=True
        check_exit(e)
    if flip:
        screen.fill((100,100,100))
    gp=pygame.mouse.get_pressed()
    psel = placers[selected]
    if (gp[0] or gp[2]) and (psel.continous or any((e.type==pygame.MOUSEBUTTONDOWN for e in es))):
        if r.collidepoint(mx, my):
            ppos = ((mx - r.left) // scale, (my - r.top) // scale)
            if psel.multi and gp[0]:
                if ppos not in multipos and (not multipos or D.dist(ppos,multipos[-1])<=1 or not psel.contiguous):
                    multipos.append(ppos)
            else:
                if gp[0]:
                    psel.place(b, ppos)
                else:
                    if multipos:
                        multipos=[]
                    psel.dest(b, ppos)
    elif multipos:
        if psel.multi:
            psel.place(b,multipos)
        multipos=[]
    ss.fill((200,200,200))
    bss.fill((150,150,150))
    pss.fill((250,250,250))
    for n,bu in enumerate(buttons):
        bu.draw(bss,b,n*64,0)
    for n,p in enumerate(placers):
        pss.blit(p.img[3],(n//16*64,n%16*64))
        if n==selected:
            pss.blit(selimg[3], (n//16*64,n%16*64))
    b.render(ss)
    sr=Img.bcentrex(Img.savfont,savename+".lvl",screen,screen.get_height()-32,(255,0,0) if saving else (0,0,0))
    if multipos:
        for mpos in multipos:
            ss.blit(selimg[scale//16-1],tuple(m*scale for m in mpos))
    else:
        if r.collidepoint(mx, my):
            ss.blit((psel.img if psel.selicon else selimg)[scale//16-1],((mx-r.left)//scale*scale,(my-r.top)//scale*scale))
    if flip:
        pygame.display.flip()
    else:
        pygame.display.update((r,br,sr,pr))
        screen.fill((100,100,100),sr)
    clock.tick(60)