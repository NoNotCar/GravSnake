__author__ = 'NoNotCar'
import pygame
import os
from random import choice
import math
import colorsys
from itertools import count
tau=math.pi*2
hpi=math.pi/2

np = os.path.normpath
loc = os.getcwd() + "/Assets/"
pygame.mixer.init()
class ScaledImage(object):
    def __init__(self,img):
        self.imgs=(img,)+tuple(xn(img,n) for n in (2,3,4))
        self.img=img
        self.h,self.w=img.get_height(),img.get_width()
    def blit(self,other,tpos,**kwargs):
        for n,i in enumerate(self.imgs):
            i.blit(other.imgs[n],(tpos[0]*(n+1),tpos[1]*(n+1)),**kwargs)
    def copy(self):
        return ScaledImage(self.img.copy())
    def __getitem__(self, item):
        return self.imgs[item]
def convertx(i):
    return i.convert_alpha()
    """px=pygame.PixelArray(i)
    for p in px:
        for n in p:
            if i.unmap_rgb(n)[3]!=255:
                del px
                return i.convert_alpha()
    else:
        del px
        return i.convert()"""
def img(fil):
    return convertx(pygame.image.load(np(loc + fil + ".png")))
def imgx(fil):
    i=img(fil)
    return ScaledImage(i)
def imgn(fil,n):
    return xn(img(fil),n)
def xn(img,n):
    return pygame.transform.scale(img,(int(img.get_width()*n),int(img.get_height()*n))).convert_alpha()
def ftrans(f,folder):
    return lambda x: f(folder+"/"+x)
def imgsz(fil, sz):
    return pygame.transform.scale(pygame.image.load(np(loc + fil + ".png")), sz).convert_alpha()

def imgstripx(fil):
    i = img(fil)
    imgs = []
    h=i.get_height()
    for n in range(i.get_width() // h):
        imgs.append(ScaledImage(i.subsurface(pygame.Rect(n * h, 0, h, h))))
    return imgs
def tilemapx(fil):
    i = img(fil)
    imgs = []
    sz=16
    h=i.get_height()
    w=i.get_width()
    for y in range(h // sz):
        for x in range(w // sz):
            imgs.append(ScaledImage(i.subsurface(pygame.Rect(x * sz, y*sz, sz, sz))))
    return imgs
def tilesplit(tile):
    img=tile[0]
    sss=[]
    for y in range(2):
        for x in range(2):
            sss.append(ScaledImage(img.subsurface(pygame.Rect(x*8,y*8,8,8))))
    return sss
class UltraTiles(object):
    blank=imgx("Blank")
    def __init__(self,fil,cc=False):
        tiles=imgstripx(fil)
        if cc:
            [colswap(t,(128,128,128),cc) for t in tiles]
        self.tiles=[tilesplit(t) for t in tiles]
        self.cache={}
    def __getitem__(self, item):
        try:
            return self.cache[item]
        except KeyError:
            tile=self.blank.copy()
            for n,t in enumerate(item):
                tile.blit(self.tiles[t][n],(n%2*8,n//2*8))
            self.cache[item]=tile
            return tile

def imgstrip(fil):
    i = img(fil)
    imgs = []
    h=i.get_height()
    for n in range(i.get_width() // h):
        imgs.append(i.subsurface(pygame.Rect(n * h, 0, h, h)).convert_alpha())
    return imgs
def imgstrip4f(fil,w):
    i = img(fil)
    imgs = []
    h=i.get_height()
    for n in range(i.get_width() // w):
        imgs.append(pygame.transform.scale(i.subsurface(pygame.Rect(n * w, 0, w, h)), (w*4, h*4)).convert_alpha())
    return imgs
def imgstrip4fs(fil,ws):
    i = img(fil)
    imgs = []
    h = i.get_height()
    cw=0
    for w in ws:
        imgs.append(pygame.transform.scale(i.subsurface(pygame.Rect(cw, 0, w, h)), (w * 4, h * 4)).convert_alpha())
        cw+=w
    return imgs
def imgrot(i):
    imgs=[i]
    for n in range(3):
        imgs.append(ScaledImage(pygame.transform.rotate(i[0],-90*n-90)))
    return imgs
def irot(i,n):
    return ScaledImage(pygame.transform.rotate(i.img,-90*n))

def musplay(fil,loops=-1):
    if fil[:3]=="EMX":
        pygame.mixer.music.load(np(loc+"EMX/" + fil[3:]+".ogg"))
    else:
        pygame.mixer.music.load(np(loc+"Music/" + fil+".ogg"))
    pygame.mixer.music.play(loops)


def bcentre(font, text, surface, offset=0, col=(0, 0, 0), xoffset=0):
    render = font.render(str(text), True, col)
    textrect = render.get_rect()
    textrect.centerx = surface.get_rect().centerx + xoffset
    textrect.centery = surface.get_rect().centery + offset
    return surface.blit(render, textrect)

def bcentrex(font, text, surface, y, col=(0, 0, 0), xoffset=0):
    render = font.render(str(text), True, col)
    textrect = render.get_rect()
    textrect.centerx = surface.get_rect().centerx + xoffset
    textrect.top = y
    return surface.blit(render, textrect)
def bcentrerect(font, text, surface, rect, col=(0, 0, 0)):
    render = font.render(str(text), True, col)
    textrect = render.get_rect()
    textrect.centerx = rect.centerx
    textrect.centery = rect.centery
    return surface.blit(render, textrect)
def cxblit(source, dest, y, xoff=0):
    srect=source.get_rect()
    drect=dest.get_rect()
    srect.centerx=drect.centerx+xoff
    srect.top=y
    return dest.blit(source,srect)
def bcentrepos(font,text,surface,cpos,col=(0,0,0)):
    render = font.render(str(text), True, col)
    textrect = render.get_rect()
    textrect.center=cpos
    return surface.blit(render, textrect)
def sndget(fil):
    return pygame.mixer.Sound(np(loc+"Sounds/"+fil+".wav"))

def hflip(img):
    return ScaledImage(pygame.transform.flip(img.img,1,0))
def xn(img,n):
    return pygame.transform.scale(img,(img.get_width()*n,img.get_height()*n))
def x4(img):
    return xn(img,4)

def fload(fil,sz=16):
    return pygame.font.Font(np(loc+fil+".ttf"),sz)
def create_man(col):
    imgs=imgstripx("Man")
    for i in imgs:
        pygame.draw.rect(i,col,pygame.Rect(20,32,24,28))
    return imgs
# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawTextRect(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text
def colswap(img,sc,ec):
    if isinstance(img,pygame.Surface):
        px=pygame.PixelArray(img)
        px.replace(sc,ec)
    else:
        for i in img.imgs:
            px = pygame.PixelArray(i)
            px.replace(sc, ec)
    return img
def colcopy(i,sc,ec):
    i=i.imgs[0].copy()
    colswap(i,sc,ec)
    return ScaledImage(i)
def darker(col,fract=0.5):
    return tuple(int(c*fract) for c in col)
def lighter(col,fract=0.5):
    return tuple(int(c+(255-c)*fract) for c in col)
def multicolcopy(img,*args):
    img=colcopy(img,*args[0])
    for s,e in args[1:]:
        colswap(img,s,e)
    return img
def draw_trans_rect(surf,col,rect):
    nsurf=pygame.Surface(rect.size,pygame.SRCALPHA)
    nsurf.fill(col)
    return surf.blit(nsurf,rect.topleft)

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image
def rots(image,rots,symmetry=1):
    rotimgs=[image]
    for r in xrange(1,rots):
        rotimgs.append(rot_center(image,360.0*r/(symmetry*rots)))
    return rotimgs
def get_rot(image,r,rots,symmetry):
    return rot_center(image, 360.0 * r / (symmetry * rots))
def polplus(pos,ang,l):
    return tuple(map(sum, zip(pos, (l*math.cos(ang),l*math.sin(ang)))))
def draw_rotor(screen,center,radius,arms,angle,col,w=4):
    angle=math.radians(angle)
    for n in range(arms):
        #magic
        pygame.draw.polygon(screen,col,(polplus(center,angle-hpi,w),polplus(center,angle+hpi,w),polplus(polplus(center,angle+hpi,w),angle,radius),polplus(polplus(center,angle-hpi,w),angle,radius)))
        angle+=tau/arms
def convimgs(image,rep,speed):
    belt=image.subsurface(pygame.Rect(4,0,56,64))
    convs=[imgrot(image)]
    for n in range(speed,rep*4,speed):
        nimg=image.copy()
        nimg.blit(belt,(4,-n))
        nimg.blit(belt,(4,64-n))
        convs.append(imgrot(nimg))
    return convs
imss=[]
class ImageManager(object):
    def __init__(self):
        self.imgs={}
        imss.append(self)
    def register(self):
        used=self.imgs.keys()
        return next((n for n in count() if n not in used))
    def gen_img(self):
        return None
    def __getitem__(self, item):
        try:
            return self.imgs[item]
        except KeyError:
            ni=self.gen_img()
            self.imgs[item]=ni
            return ni
    def reload(self):
        self.imgs={}
class RandomImageManager(ImageManager):
    def __init__(self,imgs,cf,sc=(128,128,128)):
        self.i=imgs
        self.cf=cf
        self.sc=sc
        ImageManager.__init__(self)
    def gen_img(self):
        return colcopy(choice(self.i),self.sc,self.cf())
class UTImageManager(ImageManager):
    def __init__(self,fil,cf):
        self.fil=fil
        self.cf=cf
        ImageManager.__init__(self)
    def gen_img(self):
        return UltraTiles(self.fil,self.cf())
numerals=imgstrip4fs("Numbers",[5,3]+[5]*8)
def draw_num(surf,n,pos):
    if n<1:
        return None
    n=str(n)
    x=60
    for d in reversed(n):
        x-=8 if int(d)==1 else 16
        surf.blit(numerals[int(d)], (pos[0]+x, pos[1]+36))
savfont=fload("SFont",32)
bfont=fload("cool",64)
mfont=fload("cool",32)
sfont=fload("cool",16)
music_mix={}
def musload(d):
    emx=os.listdir(np(loc+"EMX/"+d))
    emx=[e[:-4] for e in emx if e[-4:]==".ogg"]
    if emx:
        music_mix[d]=["EMX/"+d+"/"+e for e in emx]
    else:
        mus = os.listdir(np(loc + "Music/" + d))
        mus = [m[:-4] for m in mus if m[-4:] == ".ogg"]
        music_mix[d] = ["Music/"+d+"/" + m for m in mus]
class DJ(object):
    def __init__(self):
        self.songs=music_mix["Chr"]
        self.state="Chr"
    def switch(self,d):
        if self.state!=d:
            try:
                self.songs=music_mix[d]
            except KeyError:
                musload(d)
                self.songs = music_mix[d]
            pygame.mixer.music.stop()
            musplay(choice(self.songs), 1)
            self.state=d
    def update(self):
        if not pygame.mixer.music.get_busy():
            musplay(choice(self.songs),1)
#dfont=fload("PressStart2P")