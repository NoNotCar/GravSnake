import pygame

pygame.init()
pygame.font.init()
ssize=pygame.display.list_modes()[0]
screen = pygame.display.set_mode(ssize,pygame.FULLSCREEN)
clock=pygame.time.Clock()
import Img
import pickle
import os
done=False
levels = os.listdir(Img.np(Img.loc + "Levels"))
levels = [l[:-4] for l in levels if l[-4:] == ".lvl"]
updict={1:0,2:1,4:2,8:3,0:None}
def upgrade(b):
    for t in b.itertiles():
        pass
for l in levels:
    with open(Img.np(Img.loc + "Levels/%s.lvl" % l)) as s:
        b = pickle.load(s)
        upgrade(b)
    with open(Img.np(Img.loc + "Levels/%s.lvl" % l), "w") as s:
        pickle.dump(b,s)
