import pygame, sys
pygame.init()
pygame.font.init()
ssize=pygame.display.list_modes()[0]
screen = pygame.display.set_mode(ssize,pygame.FULLSCREEN)
clock=pygame.time.Clock()
import Img
import pickle
import Board
from LevelRunner import run,lselect
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
    lname=lselect(screen,levels)
    if lname is None:
        sys.exit()
    while True:
        scale=64
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

