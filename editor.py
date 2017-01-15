import pygame, sys
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1920,1080),pygame.FULLSCREEN)
clock=pygame.time.Clock()
import Board, Img
import EditorButtons as B
import pickle
import Tiles
import Direction as D
from Snake import Snake,IronSnake,AntiSnake
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
buttons=[B.Resizer(0),B.Resizer(1),B.Scaler(),B.PlayButton()]
placers=[B.TerrainPlacer(Tiles.Dirt),B.TerrainPlacer(Tiles.Snow),B.TerrainPlacer(Tiles.WoodPlatform),B.TerrainPlacer(Tiles.Portal),
         B.SnakePlacer(Snake),B.SnakePlacer(AntiSnake),B.SnakePlacer(IronSnake),B.TerrainPlacer(Tiles.Fruit),B.TerrainPlacer(Tiles.Spikes),
         B.BlockPlacer(),B.CloudBlockPlacer(),B.SpikeBlockPlacer(),B.CheesePlacer()]
br=pygame.Rect(0,0,len(buttons)*64,64)
br.centerx=screen.get_rect().centerx
bss=screen.subsurface(br)
pr=pygame.Rect(0,0,len(placers)//16*64+64,min(len(placers)*64,1024))
pr.centery=screen.get_rect().centery
pss=screen.subsurface(pr)
selected=0
selimg=Img.imgx("Select")
screen.fill((100,100,100))
pygame.display.flip()
saving=False
savename="Levels/test"
multipos=[]
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
                placers[selected].scroll()
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
                        pb.prepare()
                        run(pb,screen,ss,r)
                    # elif m.task=="Solve":
                    #     sb = deepcopy(b)
                    #     s=Board.Solver(sb)
                    #     screen.fill((100,100,100))
                    #     uprate=1
                    #     try:
                    #         while True:
                    #             for e in pygame.event.get():
                    #                 check_exit(e)
                    #             screen.fill((100, 100, 100))
                    #             Img.bcentre(Img.savfont,"STATES: "+str(len(s.states)),screen)
                    #             Img.bcentre(Img.savfont, "TESTED: " + str(len(s.past_states)), screen, 50)
                    #             Img.bcentre(Img.savfont, "UPDATE RATE: " + str(uprate), screen,100)
                    #             for _ in xrange(uprate):
                    #                 s.update()
                    #             pygame.display.flip()
                    #             clock.tick(60)
                    #             if clock.get_fps()>10:
                    #                 uprate+=1
                    #     except Board.Solution as se:
                    #         sb = deepcopy(b)
                    #         sb.prepare()
                    #         back = (100, 255, 255)
                    #         screen.fill(tuple(c * 0.5 for c in back))
                    #         pygame.display.flip()
                    #         try:
                    #             while True:
                    #                 es = pygame.event.get()
                    #                 for e in es:
                    #                     check_exit(e)
                    #                 ss.fill(back)
                    #                 sb.execute_move(se.solution.pop(0))
                    #                 sb.render(ss)
                    #                 pygame.display.update(r)
                    #                 pygame.time.wait(500)
                    #         except Board.GameEnd as error:
                    #             pass
                    #     except Board.ImpossibleException:
                    #         pass
                    flip=True
            elif pr.collidepoint(mx,my):
                selected=(my-pr.top)//64+mx//64*16
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
    if gp[0] or gp[2]:
        if r.collidepoint(mx, my):
            ppos = ((mx - r.left) // scale, (my - r.top) // scale)
            if placers[selected].multi:
                if ppos not in multipos and (not multipos or D.dist(ppos,multipos[-1])<=1 or not placers[selected].contiguous):
                    multipos.append(ppos)
            else:
                if gp[0]:
                    placers[selected].place(b,ppos)
                else:
                    placers[selected].dest(b, ppos)
    elif multipos and not (pygame.key.get_mods()&pygame.KMOD_LSHIFT and not placers[selected].contiguous):
        psel=placers[selected]
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
    """if r.collidepoint(mx, my):
        ss.blit(er.img,((mx-r.left)//64*64,(my-r.top)//64*64))"""
    sr=Img.bcentrex(Img.savfont,savename+".lvl",screen,screen.get_height()-32,(255,0,0) if saving else (0,0,0))
    for mpos in multipos:
        ss.blit(selimg[scale//16-1],tuple(m*scale for m in mpos))
    if flip:
        pygame.display.flip()
    else:
        pygame.display.update((r,br,sr,pr))
        screen.fill((100,100,100),sr)
    clock.tick(60)