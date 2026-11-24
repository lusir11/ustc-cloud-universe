"""Build the layered flowering crown at (7.15, 130.45), next to the tall cherry."""
import math
from pathlib import Path
import random
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_as06_cherry as kit

rng = random.Random(113064)
up = Vector((0, 0, 1))
tau = math.tau


def blossom_spray_atlas():
    # Four transparent sprays painted at twig scale: sun, half light, shade and tips.
    size = 512
    atlas = np.zeros((size*2,size*2,4), dtype=np.float32)
    palettes = [
        ((250,205,216),(255,235,235),(210,148,177)),
        ((231,165,194),(251,206,217),(192,130,167)),
        ((184,133,175),(227,177,202),(145,103,155)),
        ((244,188,210),(255,222,235),(202,146,178)),
    ]
    for cell,(base,edge,shade) in enumerate(palettes):
        tile = np.zeros((size,size,4),np.float32)
        tile[:,:,:3] = np.array(base)/255
        def brush(cx,cy,rx,ry,angle,color,petal=False):
            R = max(rx,ry)+2
            x0,x1 = max(0,int(cx-R)),min(size,int(cx+R+1))
            y0,y1 = max(0,int(cy-R)),min(size,int(cy+R+1))
            if x1<=x0 or y1<=y0: return
            y,x = np.ogrid[y0:y1,x0:x1]
            dx,dy = x+.5-cx,y+.5-cy
            c,s = math.cos(angle),math.sin(angle)
            u,v = (dx*c+dy*s)/rx,(dy*c-dx*s)/ry
            dist = u*u+v*v
            if petal:
                dist += .13*np.exp(-((v/.20)**2)) * np.maximum(u,0)**3
            mask = dist<=1
            region = tile[y0:y1,x0:x1]
            light = np.clip(.93+.073*u+.045*v,0,1.08)
            region[mask,:3] = (np.array(color)/255*light[...,None])[mask]
            region[mask,3] = 1

        def stroke(a,b,width,color):
            dx,dy = b[0]-a[0], b[1]-a[1]
            brush((a[0]+b[0])/2,(a[1]+b[1])/2,math.hypot(dx,dy)/2+width,width,math.atan2(dy,dx),color)

        def floret(x,y,r):
            rot = rng.random()*tau
            for k in range(5):
                a = rot+k*tau/5+rng.uniform(-.09,.09)
                tint = (.32+.5*max(0,math.sin(a)))*rng.uniform(.8,1)
                color = np.array(base)*(1-tint)+np.array(edge)*tint
                brush(x+math.cos(a)*r*.46,y+math.sin(a)*r*.46,r*.56,r*.39,a,color,True)
            brush(x,y,r*.19,r*.16,rot,shade)
            brush(x+r*.06,y+r*.07,r*.073,r*.065,rot,(244,201,164))

        wood = tuple(np.array(shade)*.67)
        knots = [(98,32),(168,103),(207,191),(285,275),(326,375),(395,462)]
        flowers = []
        for i,(a,b) in enumerate(zip(knots,knots[1:])):
            stroke(a,b,3.1-i*.39,wood)
            for k in range(3):
                f = .21+.27*k
                x,y = a[0]*(1-f)+b[0]*f,a[1]*(1-f)+b[1]*f
                side = (-1)**(i+k)
                length = rng.uniform(35,100)*(1.15-i*.075)
                tip = (x+side*length, y+rng.uniform(24,61))
                bend = (x+side*length*.58,y+16)
                stroke((x,y),bend,1.9,wood)
                stroke(bend,tip,1.15,wood)
                for j in range(4):
                    t = rng.uniform(.28,1)
                    fx,fy = x+(tip[0]-x)*t,y+(tip[1]-y)*t
                    fx += rng.uniform(-12,12)
                    fy += rng.uniform(-6,10)
                    size_flower = rng.uniform(11,19)
                    if j%2==0:
                        brush(fx+side*9,fy+6,14,4.5,.6*side,shade)
                    flowers.append((fx,fy,size_flower))
        for x,y,r in sorted(flowers,key=lambda v:v[1]):
            floret(x,y,r)
        row,col = divmod(cell,2)
        atlas[row*size:(row+1)*size,col*size:(col+1)*size] = tile
    image = bpy.data.images.new("AS06_PaintedFlowerSprays",width=size*2,height=size*2,alpha=True)
    image.pixels.foreach_set(atlas.ravel())
    image.pack()
    return image


def direction(angle):
    return Vector((math.cos(angle), math.sin(angle), 0))


def canopy_spray(base, axis, width, tile):
    # A curved, slightly folded sheet follows its shoot in 3D. The painted main
    # stem starts at atlas UV (0.19, 0.06); anchor that point on the real branch.
    base = kit.crown_position(base)
    tangent = axis.normalized()
    across = tangent.cross(up)
    if across.length < .01:
        across = Vector((1,0,0))
    across.normalize()
    twist = rng.uniform(-1.15,1.15)
    across = across*math.cos(twist)+tangent.cross(across)*math.sin(twist)
    normal = across.cross(tangent).normalized()
    rows = []
    for v in (0,.5,1):
        row = []
        for u in (0,.5,1):
            offset = across*((u-(.19+.58*v))*width)
            offset += normal*(math.sin(v*math.pi)*.072-(u-.5)**2*.10)
            pos = base + axis*(v-.06) + offset
            uv = ((tile%2+.003+.994*u)/2,(tile//2+.003+.994*v)/2)
            row.append(petals.vertex(pos,uv=uv))
        rows.append(row)
    for j in range(2):
        for i in range(2):
            petals.faces.append((rows[j][i],rows[j][i+1],rows[j+1][i+1],rows[j+1][i]))


def flowering_bough(base, heading, reach, lift, depth, arch=0.0):
    forward = direction(heading)
    lateral = direction(heading+math.pi/2)
    path = [base,base+forward*reach*.30+up*(lift*.45+.10+arch*.5),
            base+forward*reach*.68+lateral*rng.uniform(-.18,.18)+up*(lift*.81+arch),
            base+forward*reach+up*lift]
    kit.limb(kit.twigs,path,[.040,.026,.012,.003],7)
    for k in range(8):
        start = kit.along(path,.13+.117*k)
        angle = heading+(-1 if k%2 else 1)*rng.uniform(.39,1.55)
        d = direction(angle)
        end = start+d*rng.uniform(.39,.85)+up*rng.uniform(-.24,.42)
        mid = start.lerp(end,.5)+up*.085
        kit.limb(kit.twigs,[start,mid,end],[.010,.005,.0016],5)
        for j in range(7):
            anchor = kit.along([start,mid,end],.08+.143*j)
            fw = direction(angle+(-1)**j*rng.uniform(.3,1.33))
            axis = fw*rng.uniform(.42,.91)+up*rng.uniform(-.31,.59)
            value = rng.random()*.52+depth*.48 + (anchor.z-4.7)*.13
            cell = 0 if value>.85 else 3 if value>.62 else 1 if value>.36 else 2
            canopy_spray(anchor,axis,rng.uniform(.42,.85),cell)


bpy.ops.wm.read_factory_settings(use_empty=True)
kit.rng.seed(1197)
kit.CROWN_SHOULDER = (4.10, 5.82)
kit.bark = kit.Surface("AS06_AnimeBark")
kit.twigs = kit.Surface("AS06_AnimeBranches")
kit.bark_color = np.array(kit.linear((91,71,82)))
kit.wash_color = np.array(kit.linear((170,165,163)))
petals = kit.Surface("AS06_AnimeFlowerSprays")
trunk = [Vector(v) for v in [(0,0,0),(.05,0,.18),(.06,.03,.83),(.12,-.04,1.34),(.26,-.02,1.91),(.14,.03,2.36)]]
kit.limb(kit.bark,trunk,[.25,.22,.19,.18,.151,.118],16)
for i in range(6):
    d = direction(i*tau/6+.2)
    kit.limb(kit.bark,[trunk[1],d*.23+up*.073,d*.43+up*.015],[.115,.078,.008],8)
# Keep the lower fans and let the two upper leaders sweep out in different
# directions. Reserve the notch between them for glimpses of sky from the road.
scaffolds = {}
for deg, reach, top, fork, bow in [(12,3.09,3.53,3,.42),(95,2.89,3.94,4,-.34),
        (174,3.24,3.68,3,-.46),(230,1.98,5.22,4,.52),(277,3.01,3.79,3,.32),(322,1.22,6.05,5,-.38)]:
    a = math.radians(deg)
    d, side = direction(a),direction(a+math.pi/2)
    root = trunk[fork]
    path = [root]
    for t,h,kink in [(.22,.23,.08),(.44,.43,-.14),(.57,.70,-.08),(.78,.85,.13),(1,1,.08)]:
        rise = 1-(1-t)**2+.13*math.sin(math.pi*t) if top<4 else h
        path.append(root+d*(reach*t)+side*(bow*math.sin(t*math.pi)+kink)+up*((top-root.z)*rise))
    kit.limb(kit.bark,path,[.135,.106,.083,.061,.038,.014],10)
    scaffolds[deg] = path
    for j in range(8):
        t = min(.99,.30+.101*j+rng.uniform(-.025,.025))
        spread = rng.uniform(.40,1.58)*(-1 if j%2 else 1)
        narrowing = 1-.38*t if top>5 else 1.0
        length = rng.uniform(.73,1.42)*narrowing
        rise = rng.uniform(.22,.84)
        if top<4 and j in (3,5):
            # Upright interior shoots bridge the low fringe and the leader.
            length *= .74
            rise += .98 if j==3 else .73
        flowering_bough(kit.along(path,t),a+spread,length,rise,t)
    flowering_bough(path[-1],a,.66 if top>5 else .91,.36,1)
    if top>5:
        for t,spread in [(.46,1.9),(.76,-1.85)]:
            flowering_bough(kit.along(path,t),a+spread,1.03,.37,t)

# Add flowers to the shoulders and hanging edges rather than uniformly packing
# the crown. The two longer arcs create a rising rim and a trailing silhouette.
atlas_state = rng.getstate()
for limb_deg, attach, heading, reach, lift, arch in [
        (322,.78,75,2.12,.29,.27),(322,.90,145,1.69,.40,.18),
        (322,.58,26,1.82,.82,.18),(230,.84,231,1.58,.06,.34),
        (230,.67,176,1.68,.75,.15),(95,.64,99,1.49,.92,.22),
        (174,.88,211,1.20,-.37,.30),(12,.80,41,1.26,-.28,.25)]:
    flowering_bough(kit.along(scaffolds[limb_deg],attach),math.radians(heading),
                    reach,lift,attach,arch)
rng.setstate(atlas_state)
kit.bark.finish()
kit.twigs.finish()
petals.finish(blossom_spray_atlas())
kit.save_asset("sakura_tree_as06_anime")
