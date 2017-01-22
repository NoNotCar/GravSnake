import pygame,sys
from copy import deepcopy
import Board,Img
clock=pygame.time.Clock()
def check_exit(event):
    if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
        return True
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
                    return True
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
            Img.bcentre(Img.bfont, "FOOL" if fail else "YAY", screen, col=(255, 255, 255) if fail else (0, 0, 0))
            pygame.display.flip()
            pygame.time.wait(1000 if fail else 2000)
            if e.code == "FAIL":
                del undos[-2:-1]
                b = deepcopy(undos[-1])
                screen.fill(tuple(c * 0.5 for c in back))
                pygame.display.flip()
            elif not fail:
                return True
            else:
                break
def run_wm(wm, screen, ss, r):
    back = wm.back
    screen.fill(tuple(c * 0.5 for c in back))
    pygame.display.flip()
    while True:
        es = pygame.event.get()
        for e in es:
            if check_exit(e):
                return True
        mx, my = pygame.mouse.get_pos()
        wm.update(es, (mx - r.left) // wm.rscale, (my - r.top) // wm.rscale)
        wm.render(ss)
        # sr=Img.bcentrex(Img.savfont, lname, screen, screen.get_height() - 32, (0, 0, 0))
        pygame.display.update(r)
        clock.tick(60)
def lselect(screen,levels):
    maxscroll = len(levels) * 64 + 64 - screen.get_height()
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
                    selected = (mpos[1] + scroll) // 64 - 1
                    if selected >= 0 and len(levels) > selected:
                        clevel = levels[selected]
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and scroll:
            scroll -= 4
        elif keys[pygame.K_DOWN] and scroll < maxscroll:
            scroll += 4
        screen.fill((200, 200, 200))
        Img.bcentrex(Img.bfont, "SELECT LEVEL", screen, -16 - scroll)
        for n, l in enumerate(levels):
            pygame.draw.rect(screen, (200, 200, 200) if n % 2 else (150, 150, 150),
                             pygame.Rect(0, n * 64 + 64 - scroll, screen.get_width(), 64))
            Img.bcentrex(Img.savfont, l, screen, n * 64 + 80 - scroll)
        clock.tick(60)
        pygame.display.flip()
    return clevel