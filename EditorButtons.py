import Biomes
import Direction as D
import Img
import Interactives
import Tiles


class ExternalMethod(Exception):
    def __init__(self,task):
        self.task=task
# musbase=Img.imgx("Music/Icons/Base")
# musicons=[Img.imgx("Music/Icons/"+m) for m in Board.musics]
# for m in musicons:
#     m.blit(musbase,(0,0))
def bimg4(fil):
    return Img.imgx("Buttons/" + fil)
class Button(object):
    img=None
    def on_click(self,mb,board):
        pass
    def draw(self,screen,board,x,y):
        screen.blit(self.img[3],(x,y))
    def reload(self,b):
        pass
class Resizer(Button):
    imgs=bimg4("Height"),bimg4("Width")
    def __init__(self,h):
        self.h=h
    def on_click(self,mb,board):
        board.resize(self.h,mb==1)
        return True
    @property
    def img(self):
        return self.imgs[self.h]
class Scaler(Button):
    img=bimg4("Scale")
    upscale={16:32,32:48,48:64,64:64}
    downscale={64:48,48:32,32:16,16:16}
    def on_click(self,mb,board):
        if mb==1:
            board.scale=self.upscale[board.scale]
        else:
            board.scale = self.downscale[board.scale]
        return True
class ExternalButton(Button):
    def __init__(self,task):
        self.img=bimg4(task)
        self.task=task
    def on_click(self,mb,board):
        raise ExternalMethod(self.task)
class BiomeButton(Button):
    b=0
    def on_click(self,mb,board):
        self.b+=1
        self.b%=len(Biomes.biomes)
        board.biome= Biomes.biomes[self.b]
        btp.reload(board)
    def reload(self,b):
        self.b= Biomes.biomes.index(b.biome)
    @property
    def img(self):
        return Biomes.bimgs[self.b]
class Placer(object):
    img=None
    multi=False
    contiguous=True
    continous=True
    selicon=False
    def place(self,b,tpos):
        pass
    def dest(self,b,tpos):
        ts = list(b.get_ts(*tpos))
        if ts:
            b.t[tpos[0]][tpos[1]] = []
            for t in ts:
                t.on_dest(b)
            b.re_img()
    def scroll(self,d):
        pass
    def reload(self,b):
        pass
class TerrainPlacer(Placer):
    def __init__(self,tclass):
        self.tc=tclass
        self.img=tclass(0,0).img
    def place(self,b,tpos):
        ts=list(b.get_ts(*tpos))
        if len(ts)!=1 or not isinstance(ts[0],self.tc):
            b.t[tpos[0]][tpos[1]]=[self.tc(*tpos)]
            b.re_img()
class NTerrainPlacer(Placer):
    n=0
    def __init__(self,tclass,n,*exargs):
        self.tc=tclass
        self.imgs=[tclass(0,0,r,*exargs).img for r in range(n)]
        self.ns=n
        self.args=exargs
    def place(self,b,tpos):
        tx,ty=tpos
        ts=list(b.get_ts(*tpos))
        if len(ts)!=1 or not isinstance(ts[0],self.tc):
            b.t[tpos[0]][tpos[1]]=[self.tc(tx,ty,self.n,*self.args)]
            b.re_img()
    def scroll(self,d):
        self.n+=d
        self.n%=self.ns
    @property
    def img(self):
        return self.imgs[self.n]
class MTerrainPlacer(NTerrainPlacer):
    def __init__(self,*tclasses):
        self.tcs=tclasses
        self.imgs=[tc(0,0).img for tc in tclasses]
        self.ns=len(tclasses)
    def place(self,b,tpos):
        tx,ty=tpos
        ts=list(b.get_ts(*tpos))
        if len(ts)!=1 or not isinstance(ts[0],self.tcs[self.n]):
            b.t[tpos[0]][tpos[1]]=[self.tcs[self.n](tx,ty)]
            b.re_img()
class BiomeTerrainPlacer(Placer):
    def reload(self,b):
        terr=b.biome.terrain
        try:
            self.placer=NTerrainPlacer(terr[0],terr[1])
        except TypeError:
            self.placer=TerrainPlacer(terr)
    def place(self,b,tpos):
        self.placer.place(b,tpos)
    def scroll(self,d):
        self.placer.scroll(d)
    @property
    def img(self):
        return self.placer.img
btp=BiomeTerrainPlacer()
class SnakePlacer(Placer):
    multi = True
    def __init__(self,sc):
        self.head=sc.head
        self.sc=sc
        self.img=self.head.eimg
    def place(self,b,tpos):
        if len(tpos)<2:
            return None
        snake=self.sc()
        for n,(tx,ty) in enumerate(tpos[:-1]):
            ns = tpos[n + 1]
            fdire = D.dirs.index((ns[0]-tx,ns[1]-ty))
            if n:
                ls=tpos[n-1]
                bdire=D.dirs.index((ls[0]-tx,ls[1]-ty))
            s=self.head.segclass(tx,ty,bdire if n else None,fdire,snake)
            b.spawn(s)
        tx,ty=tpos[-1]
        sh=self.head(tx,ty,snake)
        b.spawn(sh)
        b.re_img()
# class SnakeFlipper(Placer):
#     img=bimg4("FlipSnake")
#     continous = False
#     def place(self,b,tpos):
#         for t in b.get_ts(*tpos):
#             if "Snake" in t.name and t.grav:
#                 t.snake.grav=-t.grav
#                 break
class BlockPlacer(Placer):
    multi = True
    contiguous = False
    img= Img.imgstripx("Tiles/GravBlock")[0]
    bc= Tiles.Block
    sc= Tiles.BGravShape
    def place(self,b,tpos):
        block=self.sc()
        for n,(tx,ty) in enumerate(tpos):
            b.spawn(self.bc(tx,ty,block))
        b.re_img()
class CloudBlockPlacer(BlockPlacer):
    img = Img.imgstripx("Tiles/CloudBlock")[0]
    bc= Tiles.CloudBlock
    sc= Tiles.GravShape
class SpikeBlockPlacer(BlockPlacer):
    img = Img.imgstripx("Tiles/SpikeBlock")[0]
    bc= Tiles.SpikeBlock
    sc= Tiles.GravShape
class CheesePlacer(BlockPlacer):
    img = Img.imgstripx("Tiles/Cheese")[0]
    bc= Tiles.Cheese
    sc= Tiles.GravShape
class JellyPlacer(BlockPlacer):
    imgs = [Interactives.Jelly.uts[n][0, 0, 0, 0] for n in range(4)]
    col=0
    def place(self,b,tpos):
        block= Tiles.GravShape()
        for n,(tx,ty) in enumerate(tpos):
            b.spawn(Interactives.Jelly(tx, ty, block, self.col))
        b.re_img()
    def scroll(self,d):
        self.col += d
        self.col %= 4
    @property
    def img(self):
        return self.imgs[self.col]
class Rotator(Placer):
    img=bimg4("Rotate")
    continous = False
    selicon = True
    def place(self,b,tpos):
        for t in b.get_ts(*tpos):
            if "Snake" in t.name and t.grav:
                t.snake.grav=-t.grav
                break
            if t.name=="XSwitch":
                t.r+=1
                t.r%=4
class Zipper(Placer):
    img=bimg4("Zip")
    continous = False
    selicon = True
    def place(self,b,tpos):
        for t in b.get_ts(*tpos):
            if "SnakeHead"==t.name:
                t.zipped=not t.zipped
                break
class BEPlacer(Placer):
    continous = False
    selicon = True
    def __init__(self,beclass):
        self.beclass=beclass
        self.img=self.beclass.eimg
    def place(self,b,tpos):
        for t in b.get_ts(*tpos):
            if isinstance(t, Tiles.Block):
                t.extension=self.beclass(t)
                break
class WMTerrainPlacer(Placer):
    def __init__(self,tclass):
        self.tc=tclass
        self.img=tclass().img
    def place(self,wm,tpos):
        t=wm.get_t(*tpos)
        if not t or not isinstance(t,self.tc):
            wm.terrain[tpos[0]][tpos[1]]=self.tc()
            wm.re_img()
    def dest(self,wm,tpos):
        t = wm.get_t(*tpos)
        if t:
            wm.terrain[tpos[0]][tpos[1]]=None
            wm.re_img()
class WMPathPlacer(Placer):
    def __init__(self,pclass):
        self.pc=pclass
        self.img=pclass.eimg
    def place(self,wm,tpos):
        p=wm.get_p(*tpos)
        if not p or not isinstance(p,self.pc):
            wm.paths[tpos[0]][tpos[1]]=self.pc()
            wm.re_img()
    def dest(self,wm,tpos):
        p = wm.get_p(*tpos)
        if p:
            wm.paths[tpos[0]][tpos[1]]=None
            wm.re_img()
class WMLevelPlacer(WMPathPlacer):
    continous = False
    def place(self,wm,tpos):
        p=wm.get_p(*tpos)
        if not p or not isinstance(p,self.pc):
            raise ExternalMethod("SelectLevel")
    def lplace(self,wm,tpos,lname):
        if lname:
            wm.paths[tpos[0]][tpos[1]] = self.pc(lname)
            wm.re_img()
    def dest(self,wm,tpos):
        p = wm.get_p(*tpos)
        if p:
            wm.paths[tpos[0]][tpos[1]]=None
            wm.re_img()

