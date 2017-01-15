import Img
import math
tau=2*math.pi #take that babby
class Biome(object):
    backcolour=(0,0,0)
    img=None
    def render_back(self,ss,b):
        pass
    def render_front(self,ss,b):
        pass
class Islands(Biome):
    backcolour = (100, 255, 255)
    water=Img.imgx("Tiles/Water")
    rx=0
    yp=0.0
    def render_front(self,ss,b):
        for x in range(b.sx+1):
            ss.blit(self.water[b.iscale],(x*b.rscale+self.rx*b.ascale//4-b.rscale,int((b.sy-0.5)*b.rscale+math.sin(self.yp)*b.rscale/4)))
        self.rx+=1
        self.rx%=64
        self.yp+=0.03
        self.yp%=tau
