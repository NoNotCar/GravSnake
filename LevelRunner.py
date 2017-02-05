from copy import deepcopy
from random import randint,choice

import pygame,sys

import Board
import Img
import WorldMap

clock=pygame.time.Clock()
downscale={64:48,48:32,32:16,16:16}
fool=["IDIOT","FAILIURE","OH DEAR","OH DEARIE ME","INCOMPETENT","HAHA","FAIL","STUPID","FOOOOOOL"]
yay=["HOORAH","SUPERB","SUCCESS","YOU WIN","AMAZING","PASS","10/10 WOULD PLAY AGAIN","COMPETENT","YAAAAAY"]
def check_exit(event):
    if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
        return True
    elif event.type==pygame.QUIT:
        sys.exit()
def run(b,screen,ss,r):
    undos=[deepcopy(b)]
    back = b.biome.backcolour
    screen.fill(tuple(c * 0.5 for c in back))
    pygame.display.flip()
    while True:
        try:
            es = pygame.event.get()
            for e in es:
                if check_exit(e):
                    return True,False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_LSHIFT and len(undos) - 1:
                    undos.pop()
                    b = deepcopy(undos[-1])
            ss.fill(back)
            mx, my = pygame.mouse.get_pos()
            uc = b.update(es, (mx - r.left) // b.rscale, (my - r.top) // b.rscale)
            if uc:
                undos.append(uc)
                if len(undos) > 100:
                    undos.pop(0)
            b.render(ss)
            # sr=Img.bcentrex(Img.savfont, lname, screen, screen.get_height() - 32, (0, 0, 0))
            pygame.display.update(r)
            clock.tick(60)
        except Board.GameEnd as e:
            fail = e.fail
            screen.fill((0, 0, 0) if fail else (255, 255, 0))
            if fail:
                msg="FOOL" if randint(0,3) else choice(fool)
            else:
                msg = "YAY" if randint(0, 3) else choice(yay)
            Img.bcentre(Img.bfont, msg, screen, col=(255, 255, 255) if fail else (0, 0, 0))
            pygame.display.flip()
            pygame.time.wait(1000 if fail else 2000)
            if e.code == "FAIL":
                b = deepcopy(undos[-1])
                screen.fill(tuple(c * 0.5 for c in back))
                pygame.display.flip()
            elif not fail:
                return True,True
            else:
                return False,False
def run_wm(wm, screen, ss, r):
    back = wm.back
    screen.fill(tuple(c * 0.5 for c in back))
    pygame.display.flip()
    Img.musplay("Map")
    while True:
        es = pygame.event.get()
        for e in es:
            if check_exit(e):
                return True
        mx, my = pygame.mouse.get_pos()
        try:
            wm.update(es, (mx - r.left) // wm.rscale, (my - r.top) // wm.rscale)
        except WorldMap.RunLevel as e:
            pygame.mixer.music.stop()
            pygame.time.wait(250)
            while True:
                scale = 64
                b=deepcopy(e.b)
                b.prepare()
                b.scale = scale
                size = b.sx, b.sy
                lr = pygame.Rect(0, 0, size[0] * scale, size[1] * scale)
                gr = screen.get_rect()
                lr.center = gr.center
                while True:
                    try:
                        lss = screen.subsurface(lr)
                        break
                    except ValueError:
                        scale = downscale[scale]
                        b.scale = scale
                        lr = pygame.Rect(0, 0, size[0] * scale, size[1] * scale)
                        lr.center = gr.center
                rcode=run(b, screen, lss, lr)
                if rcode[0]:
                    pygame.mixer.music.stop()
                    if not rcode[1]:
                        wm.cancel()
                    for im in Img.imss:
                        im.reload()
                    Img.musplay("Map")
                    break
            screen.fill(tuple(c * 0.5 for c in back))
            pygame.display.flip()
        wm.render(ss)
        # sr=Img.bcentrex(Img.savfont, lname, screen, screen.get_height() - 32, (0, 0, 0))
        pygame.display.update(r)
        clock.tick(60)
def lselect(screen,levels=(),worldmaps=()):
    maxscroll = len(levels) * 64+len(worldmaps)*64 + 64*(bool(levels)+bool(worldmaps)) - screen.get_height()
    selections=[]
    for t,l in (("#WORLDMAPS",worldmaps),("#LEVELS",levels)):
        if l:
            selections.extend([t]+l)
    scrollspeed = 32
    scroll = 0
    clevel = None
    screen.fill((200, 200, 200))
    pygame.display.flip()
    while clevel is None:
        for e in pygame.event.get():
            if check_exit(e):
                return None
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button in (4, 5):
                    nscroll = scroll + (-scrollspeed if e.button == 4 else scrollspeed)
                    if 0 <= nscroll <= maxscroll:
                        scroll = nscroll
                    elif e.button == 5:
                        scroll = maxscroll
                    else:
                        scroll = 0
                else:
                    mpos = pygame.mouse.get_pos()
                    selected = selections[(mpos[1] + scroll) // 64]
                    if selected[0]!="#":
                        clevel = selected
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and scroll:
            scroll -= 4
        elif keys[pygame.K_DOWN] and scroll < maxscroll:
            scroll += 4
        screen.fill((200, 200, 200))
        for n, s in enumerate(selections):
            pygame.draw.rect(screen, (200, 200, 200) if n % 2 else (150, 150, 150),
                             pygame.Rect(0, n * 64 + 64 - scroll, screen.get_width(), 64))
            if s[0]=="#":
                Img.bcentrex(Img.bfont, s[1:], screen, n * 64 - 16 - scroll)
            else:
                Img.bcentrex(Img.savfont, s, screen, n * 64 + 16 - scroll)
        clock.tick(60)
        pygame.display.flip()
    return clevel