import pygame, sys
pygame.init()
pygame.font.init()
ssize=pygame.display.list_modes()[0]
screen = pygame.display.set_mode(ssize,pygame.FULLSCREEN)
clock=pygame.time.Clock()
import Img
import pickle
import Board
from LevelRunner import run
import os
done=False
levels = os.listdir(Img.np(Img.loc + "Levels"))
levels = [l[:-4] for l in levels if l[-4:] == ".lvl"]
maxscroll=len(levels)*64+64-ssize[1]
scrollspeed=32
scroll=0
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
                if e.button in (4,5):
                    nscroll=scroll+(-scrollspeed if e.button==4 else scrollspeed)
                    if 0<=nscroll<=maxscroll:
                        scroll=nscroll
                    elif e.button==5:
                        scroll=maxscroll
                    else:
                        scroll=0
                else:
                    mpos=pygame.mouse.get_pos()
                    selected=(mpos[1]+scroll)//64-1
                    if selected>=0 and len(levels)>selected:
                        clevel=levels[selected]
        keys=pygame.key.get_pressed()
        if keys[pygame.K_UP] and scroll:
            scroll-=4
        elif keys[pygame.K_DOWN] and scroll<maxscroll:
            scroll+=4
        screen.fill((200,200,200))
        Img.bcentrex(Img.bfont,"SELECT LEVEL",screen,-16-scroll)
        for n,l in enumerate(levels):
            pygame.draw.rect(screen,(200,200,200) if n%2 else (150,150,150),pygame.Rect(0,n*64+64-scroll,screen.get_width(),64))
            Img.bcentrex(Img.savfont, l, screen, n*64+80-scroll)
        clock.tick(60)
        pygame.display.flip()
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
            pygame.mixer.music.stop()
            break
    for im in Img.imss:
        im.reload()

