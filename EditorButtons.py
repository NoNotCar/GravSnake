import Img
import Tiles
import Snake
import Direction as D
class ExternalMethod(Exception):
    def __init__(self,task):
        self.task=task
def bimg4(fil):
    return Img.imgx("Buttons/" + fil)
class Button(object):
    img=None
    def on_click(self,mb,board):
        pass
    def draw(self,screen,board,x,y):
        screen.blit(self.img[3],(x,y))
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
class PlayButton(Button):
    img=bimg4("Play")
    def on_click(self,mb,board):
        raise ExternalMethod("Play")
class SolveButton(Button):
    img=bimg4("Solve")
    def on_click(self,mb,board):
        raise ExternalMethod("Solve")
class Placer(object):
    img=None
    multi=False
    contiguous=True
    def place(self,b,tpos):
        pass
    def dest(self,b,tpos):
        pass
    def scroll(self):
        pass
class TerrainPlacer(Placer):
    def __init__(self,tclass):
        self.tc=tclass
        self.img=tclass(0,0).img
    def place(self,b,tpos):
        ts=list(b.get_ts(*tpos))
        if len(ts)>1 or not isinstance(ts[0],self.tc):
            b.t[tpos[0]][tpos[1]]=[self.tc(*tpos)]
            b.re_img()
    def dest(self,b,tpos):
        ts = list(b.get_ts(*tpos))
        if len(ts) > 1 or not isinstance(ts[0], Tiles.Air):
            b.t[tpos[0]][tpos[1]] = [Tiles.Air(*tpos)]
            b.re_img()
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
            s=self.head.segclass(tx,ty,2**bdire if n else 0,2**fdire,snake)
            b.spawn(s)
        tx,ty=tpos[-1]
        sh=self.head(tx,ty,snake)
        b.spawn(sh)
class BlockPlacer(Placer):
    multi = True
    contiguous = False
    img=Img.imgstripx("Tiles/GravBlock")[0]
    bc=Tiles.Block
    sc=Tiles.BGravShape
    def place(self,b,tpos):
        block=self.sc()
        for n,(tx,ty) in enumerate(tpos):
            b.spawn(self.bc(tx,ty,block))
        b.re_img()
class CloudBlockPlacer(BlockPlacer):
    img = Img.imgstripx("Tiles/CloudBlock")[0]
    bc=Tiles.CloudBlock
    sc=Tiles.GravShape
class SpikeBlockPlacer(BlockPlacer):
    img = Img.imgstripx("Tiles/SpikeBlock")[0]
    bc=Tiles.SpikeBlock
    sc=Tiles.GravShape
class CheesePlacer(BlockPlacer):
    img = Img.imgstripx("Tiles/Cheese")[0]
    bc=Tiles.Cheese
    sc=Tiles.GravShape

