dirs=(0,-1),(1,0),(0,1),(-1,0)
idirf={1:4,2:8,4:1,8:2}
icorners=((-1,0),(0,-1),(-1,-1)),((1,0),(0,-1),(1,-1)),((-1,0),(0,1),(-1,1)),((1,0),(0,1),(1,1))
def get_dir(x):
    if isinstance(x,tuple):
        return x
    return dirs[x%4]
def rotate(d,x):
    i=dirs.index(d[:2])
    return dirs[(i+x)%4]+d[2:]
def flip(d):
    i = dirs.index(d[:2])
    return dirs[(i + 2) % 4] + (2-d[2],)
def rot_v(v,x):
    x=x%4
    if x==1:
        return -v[1],v[0]
    elif x==2:
        return -v[0],-v[1]
    elif x==3:
        return v[1],-v[0]
    return v
def add_vs(*vs):
    return tuple(sum(c) for c in zip(*vs))
def dist(v1,v2):
    return sum((v1[n]-v2[n])**2 for n in range(len(v1)))**0.5
def xydist(v1,v2):
    return sum(abs(v1[n]-v2[n]) for n in range(len(v1)))
def offsetpos(d,x,y,m=1):
    dire = get_dir(d)
    return x + dire[0]*m, y + dire[1]*m
def iter_offsets(x,y,dset=dirs):
    for d in dset:
        yield offsetpos(d,x,y)