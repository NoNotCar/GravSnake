import Img
import Direction as D
class Terrain(object):
    ut=None
    corners=(0,0,0,0)
    name="Terrain"
    def re_img(self,wm,x,y):
        corners = []
        for dset in D.icorners:
            corner = 0
            for n, (tx, ty) in enumerate(D.iter_offsets(x, y, dset)):
                if wm.in_world(tx,ty):
                    t=wm.get_t(tx,ty)
                    if t and t.name==self.name:
                        corner += n + 1 if n < 2 else 1
                else:
                    corner += n + 1 if n < 2 else 1
                if n == 1 and corner != 3:
                    break
            corners.append(corner)
        self.corners = tuple(corners)
    @property
    def img(self):
        return self.ut[self.corners]
class Dirt(Terrain):
    ut=Img.UltraTiles("Tiles/WMapDirt")
class Path(object):
    ut = Img.UltraTiles("WMapPath")
    corners = (0, 0, 0, 0)
    def re_img(self, wm, x, y):
        corners = []
        for dset in D.icorners:
            corner = 0
            for n, (tx, ty) in enumerate(D.iter_offsets(x, y, dset)):
                if wm.in_world(tx, ty):
                    p = wm.get_p(tx, ty)
                    if p:
                        corner += n + 1 if n < 2 else 1
                if n == 1:
                    break
            corners.append(corner)
        self.corners = tuple(corners)
    @property
    def img(self):
        return self.ut[self.corners]