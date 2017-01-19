class WorldMap(object):
    iscale = 3
    rscale = 64
    back=(0,148,255)
    def __init__(self, size, scale=64):
        self.sx, self.sy = size
        self.paths = [[None for y in range(self.sy)] for x in range(self.sx)]
        self.terrain=[[None for y in range(self.sy)] for x in range(self.sx)]
        self.re_img()
        self.scale = scale

    def render(self, screen):
        screen.fill(self.back)
        for x,y in self.iterlocs():
            t=self.get_t(x,y)
            if t:
                screen.blit(t.img[self.iscale],(x*self.scale,y*self.scale))
        for p,x,y in self.iterpaths(True):
            screen.blit(p.img[self.iscale], (x * self.scale, y * self.scale))
    def update(self, events, mx, my):
        pass
    def iterlocs(self):
        for x in range(self.sx):
            for y in range(self.sy):
                yield x, y

    def iterpaths(self, pos=False):
        if pos:
            for x, y in self.iterlocs():
                p=self.get_p(x, y)
                if p:
                    yield p,x,y
        else:
            for x, y in self.iterlocs():
                p = self.get_p(x, y)
                if p:
                    yield p
    def iterterrs(self, pos=False):
        if pos:
            for x, y in self.iterlocs():
                t=self.get_t(x, y)
                if t:
                    yield t,x,y
        else:
            for x, y in self.iterlocs():
                t = self.get_t(x, y)
                if t:
                    yield t

    def in_world(self, x, y):
        return 0 <= x < self.sx and 0 <= y < self.sy

    def get_p(self, x, y):
        if self.in_world(x, y):
            return self.paths[x][y]
    def get_t(self, x, y):
        if self.in_world(x, y):
            return self.terrain[x][y]

    def spawn(self, p):
        self.paths[p.x][p.y]=p

    def dest(self, p):
        self.paths[p.x][p.y]=p

    def resize(self, h, big):
        for array in self.paths,self.terrain:
            if h and big:
                array.append([None for _ in range(self.sy)])
            elif big:
                for x, c in enumerate(array):
                    c.append(None)
            elif h:
                array.pop()
            else:
                for c in array:
                    c.pop()
        if h:
            self.sx += 1 if big else -1
        else:
            self.sy += 1 if big else -1

    def re_img(self):
        for t,x,y in self.iterterrs(True):
            t.re_img(self,x,y)
        for p,x,y in self.iterpaths(True):
            p.re_img(self,x,y)

    @property
    def scale(self):
        return self.rscale

    @scale.setter
    def scale(self, n):
        self.rscale = n
        self.iscale = self.scale // 16 - 1
        self.ascale = self.scale // 16
