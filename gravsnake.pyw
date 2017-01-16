import pygame, sys
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(pygame.display.list_modes()[0],pygame.FULLSCREEN)
clock=pygame.time.Clock()
import Img
import pickle
import Board
from copy import deepcopy
from LevelRunner import run
import os
done=False
levels = os.listdir(Img.np(Img.loc + "Levels"))
levels = [l[:-4] for l in levels if l[-4:] == ".lvl"]
downscale={64:48,48:32,32:16,16:16}
scale=64
def check_exit(event):
    if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
        sys.exit()
while True:
    clevel = None
    screen.fill((200, 200, 200))
    pygame.display.flip()
    while clevel is None:
        for e in pygame.event.get():
            check_exit(e)
            if e.type==pygame.MOUSEBUTTONDOWN:
                mpos=pygame.mouse.get_pos()
                selected=mpos[1]//64-1
                if selected>=0 and len(levels)>selected:
                    clevel=levels[selected]
        screen.fill((200,200,200))
        Img.bcentrex(Img.bfont,"SELECT LEVEL",screen,-16)
        for n,l in enumerate(levels):
            pygame.draw.rect(screen,(200,200,200) if n%2 else (150,150,150),pygame.Rect(0,n*64+64,screen.get_width(),64))
            Img.bcentrex(Img.savfont, l, screen, n*64+80)
        clock.tick(60)
        pygame.display.update(pygame.Rect(0,0,screen.get_width(),len(levels)*64+64))
    while True:
        scale=64
        lname=clevel
        with open(Img.np(Img.loc + "Levels/%s.lvl" % lname)) as s:
            b = pickle.load(s)
            b.prepare()
            b.scale=scale
        size = b.sx, b.sy
        r = pygame.Rect(0, 0, size[0] * scale, size[1] * scale)
        gr=screen.get_rect()
        r.center = gr.center
        while True:
            try:
                ss = screen.subsurface(r)
                break
            except ValueError:
                scale=downscale[scale]
                b.scale = scale
                r = pygame.Rect(0, 0, size[0] * scale, size[1] * scale)
                gr = screen.get_rect()
                r.center = gr.center
        if run(b,screen,ss,r):
            break
    for im in Img.imss:
        im.reload()

