import math

import FX
import Img
import Tiles

tau=2*math.pi #take that babby
class Biome(object):
    backcolour=(0,0,0)
    img=None
    music= "Overworld"
    water=False
    gravity=1
    terrain=None
    def __init__(self,b):
        pass
    def render_back(self,ss,b):
        pass
    def render_front(self,ss,b):
        pass
class Islands(Biome):
    backcolour = (100, 255, 255)
    fxwater= Img.imgx("Tiles/Water")
    rx=0
    yp=0.0
    terrain = Tiles.Dirt
    def render_front(self,ss,b):
        for x in range(b.sx+1):
            ss.blit(self.fxwater[b.iscale],(x*b.rscale+self.rx*b.ascale//4-b.rscale,int((b.sy-0.5)*b.rscale+math.sin(self.yp)*b.rscale/4)))
        self.rx+=1
        self.rx%=64
        self.yp+=0.03
        self.yp%=tau
class PinkIslands(Islands):
    backcolour = (238,204,255)
    fxwater = Img.imgx("Tiles/PinkWater")
    terrain = Tiles.PinkDirt
    music="Overworld2"
class Alien(Biome):
    backcolour = (255, 127, 237)
    fxwater = Img.imgx("Tiles/AFog")
    yp = 0.0
    music = "Glowsphere"
    terrain = Tiles.Hex, 4
    def render_front(self, ss, b):
        for x in range(b.sx):
            ss.blit(self.fxwater[b.iscale], (x * b.rscale,int((b.sy - 0.75) * b.rscale + math.sin(self.yp) * b.rscale / 8)))
        self.yp += 0.03
        self.yp %= tau
class Snow(Biome):
    backcolour = (150,200,200)
    music="Snow"
    terrain = Tiles.Snow
    def __init__(self,b):
        self.fxl= FX.FXLayer([FX.Mountain(b) for _ in range(b.sx // 2)])
        self.sfx= FX.RFXLayer(FX.BackSnow, 0.02, b)
        self.fsfx= FX.RFXLayer(FX.Snow, 0.01, b)
    def render_back(self,ss,b):
        self.fxl.render(ss,b)
        self.sfx.render(ss,b)
    def render_front(self,ss,b):
        self.fsfx.render(ss,b)
class Underwater(Biome):
    backcolour = (0, 74, 127)
    fxwater= Img.imgx("Tiles/AntiWater")
    rx=0
    yp=0.0
    music = "Underwater"
    water=True
    terrain = Tiles.SeaBlock
    def __init__(self,b):
        self.swfx= FX.DFXLayer(FX.Seaweed, 1, b, i_y=True)
    def render_back(self,ss,b):
        for x in range(b.sx+1):
            ss.blit(self.fxwater[b.iscale],(x*b.rscale+self.rx*b.ascale//4-b.rscale,-0.5*b.rscale+math.sin(self.yp)*b.rscale/4))
        self.rx+=1
        self.rx%=64
        self.yp+=0.03
        self.yp%=tau
        self.swfx.render(ss,b)
class Special(Biome):
    backcolour = (6,)*3
    music="Critical"
    terrain = Tiles.Hex, 4
    def __init__(self,b):
        self.starfx= FX.DFXLayer(FX.RotoStar, 0.2, b)
        self.beamfx= FX.DFXLayer(FX.BeamFX, 0.5, b, i_y=True)
    def render_back(self,ss,b):
        self.starfx.render(ss,b)
        self.beamfx.render(ss,b)
class Starry(Biome):
    backcolour = (0,0,16)
    music="SpacetimeDX"
    terrain = Tiles.Asteroid
    gravity = 0
    def __init__(self,b):
        self.starfx= FX.DFXLayer(FX.Star, 0.2, b,args=((200,200,255),))
    def render_back(self,ss,b):
        self.starfx.render(ss,b)
biomes=Islands,Snow,Underwater,Alien,PinkIslands,Starry,Special
bimgs=[Img.imgx("B_" + b.__name__) for b in biomes]
