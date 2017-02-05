import sys
import config
import pygame

pygame.init()
pygame.font.init()
ssize=config.force_resolution if config.force_resolution else pygame.display.list_modes()[0]
if config.fullscreen:
    screen = pygame.display.set_mode(ssize,pygame.FULLSCREEN)
else:
    screen=pygame.display.set_mode(ssize)
clock=pygame.time.Clock()
import Img
import pickle
from LevelRunner import run,lselect,run_wm
import os
done=False
saved = os.listdir(Img.np(Img.loc + "Levels"))
levels = [l[:-4] for l in saved if l[-4:] == ".lvl"]
worldmaps=[l[:-4] for l in saved if l[-4:] == ".gwm"]
downscale={64:48,48:32,32:16,16:16}
scale=64
def check_exit(event):
    if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE or event.type==pygame.QUIT:
        sys.exit()
while True:
    lname=lselect(screen,levels,worldmaps)
    if lname is None:
        sys.exit()
    wm=lname in worldmaps
    while True:
        scale=64
        with open(Img.np(Img.loc + "Levels/%s%s" % (lname, (".gwm" if wm else ".lvl")))) as s:
            b = pickle.load(s)
            if wm:
                try:
                    with open(Img.np(Img.loc + "Save/%s.sav" % lname)) as s:
                        completed=pickle.load(s)
                except IOError:
                    completed=set()
                b.prepare(lname,completed)
            else:
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
        if wm:
            if run_wm(b,screen,ss,r):
                sys.exit()
        elif run(b,screen,ss,r)[0]:
            pygame.mixer.music.stop()
            break
    for im in Img.imss:
        im.reload()

