import pygame,sys
from copy import deepcopy
import Board,Img
clock=pygame.time.Clock()
def check_exit(event):
    if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
        return True
def run(b,screen,ss,r):
    undos=[deepcopy(b)]
    back = (100, 255, 255)
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
            uc = b.update(es, (mx - r.left) // 64, (my - r.top) // 64)
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