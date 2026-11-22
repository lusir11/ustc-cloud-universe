"""Build the connected sports/B, humanities A and museum C wings from reference photographs.
Input coordinates are campus east, south, height (metres). Meshes are batched by wing and finish.
Run with Python 3, numpy and Pillow. The generated Godot assets share one local origin.
"""
import io
import json
import math
import struct
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import humanities_finishes as finishes

HERE = Path(__file__).resolve().parent
CAMPUS = HERE.parents[1]
OUTPUT = CAMPUS / "godot/assets/models"
ORIGIN = (-310, 530)
BRICKS = {"brick", "rose"}
COLORS = {
    "brick":"#9b533f", "rose":"#ac6855", "stone":"#bbb6a5", "concrete":"#a39e96",
    "ivory":"#ded5bd", "glass":"#657f8b", "glass_dark":"#334753", "metal":"#333c40",
    "roof":"#767978", "tile":"#bcb9ae", "steel":"#969e9b", "gold":"#c4a365",
    "white":"#e7e2d5", "red":"#913e39", "blue":"#324973", "dark":"#282c2b",
    "ac":"#b1b3aa", "wood":"#7a5e46",
}


def linear_rgb(color):
    vals = [int(color[i:i+2], 16)/255 for i in (1,3,5)]
    return [v/12.92 if v < .04045 else ((v+.055)/1.055)**2.4 for v in vals]


def brick_texture():
    # One 1.92 x 1.92 m repeat, 8 stretchers across and 24 courses high.
    rng = np.random.default_rng(1135360068)
    y,x = np.mgrid[:768,:768]
    row = y // 32
    shifted = (x + (row % 2)*48) % 768
    col = shifted // 96
    variation = rng.uniform(0.89, 1.09, (24,8))[row,col]
    noise = rng.normal(0,.02,(768,768))
    seams = (shifted%96 < 3) | (y%32 < 3)
    factor = np.where(seams, .64, variation) + noise
    return Image.fromarray(np.uint8(np.clip(factor*230, 0,255))).convert("RGB")


def footprint_tris(xy):
    """Ear clipping handles the concave OSM footprints and convex caps alike."""
    xy = np.array(xy, dtype=float)
    cross = lambda a,b: a[0]*b[1]-a[1]*b[0]
    pending = list(range(len(xy)))
    if sum(cross(xy[i-1], xy[i]) for i in pending) < 0:
        pending.reverse()
    triangles = []
    while len(pending)>2:
        for j,b in enumerate(pending):
            a,c = pending[j-1],pending[(j+1)%len(pending)]
            if cross(xy[b]-xy[a],xy[c]-xy[b]) < 1e-8:
                continue
            if any(min(cross(xy[v]-xy[u],xy[k]-xy[u]) for u,v in ((a,b),(b,c),(c,a))) > 1e-8
                   for k in pending if k not in (a,b,c)):
                continue
            triangles.append((a,b,c))
            pending.pop(j)
            break
        else:
            if len(pending)==3 and abs(cross(xy[pending[1]]-xy[pending[0]],xy[pending[2]]-xy[pending[0]]))<1e-8:break
            raise ValueError("Invalid footprint: "+str(xy))
    return triangles


def rectangle(cx,cy,width,depth,angle):
    c,s = math.cos(angle),math.sin(angle)
    return [(cx+dx*c-dy*s,cy+dx*s+dy*c) for dx,dy in
            ((-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2))]


class Model:
    def __init__(self):
        self.section = ""
        self.parts = defaultdict(lambda: [[],[],[],[]])
        self.materials = {}
        self.image_for = {}
        self.normal_for = {}
        self.jpeg_images = set()
        self.textures = {"brick":brick_texture()}
        self.solids = []
        self.parking = []
        self.planting = []
        for name,color in COLORS.items():
            self.material(name,color, .22 if "glass" in name else .78, .45 if name in ("steel","gold","glass","glass_dark") else 0)
        self.image_for.update({key:"brick" for key in BRICKS})
        finishes.install(self, CAMPUS)

    def material(self,name,color,roughness=.65,metallic=0.):
        self.materials[name] = {"name":name, "pbrMetallicRoughness":{
            "baseColorFactor":linear_rgb(color)+[1.],"roughnessFactor":roughness,"metallicFactor":metallic}}
        return name

    def face(self,mat,points,uv=None):
        if self.section == "CB10_AC":
            mat = finishes.FINISH.get(mat, mat)
        p=np.asarray(points,dtype=float)
        norm=np.cross(p[1]-p[0],p[2]-p[0])
        if np.linalg.norm(norm)<1e-9:return
        norm/=np.linalg.norm(norm)
        pos,nor,tex,indices=self.parts[self.section,mat]
        start=len(pos)
        if uv is None:
            axes=[0,1] if abs(norm[2])>.75 else ([1,2] if abs(norm[0])>abs(norm[1]) else [0,2])
            repeat = finishes.REPEAT_METRES.get(mat, (1.92, 1.92))
            uv=p[:,axes]/repeat
            if mat == "court_stone" and axes == [0,1]:
                uv = (p[:,axes]-[-324.65,552.11])/repeat
        for pt,t in zip(p,uv):
            pos.append([pt[0]-ORIGIN[0],pt[2],pt[1]-ORIGIN[1]])
            nor.append(norm[[0,2,1]].tolist())
            tex.append(t)
        for i in range(1,len(p)-1):
            indices.extend((start,start+i+1,start+i))

    def quad(self,name,mat,vertices):
        self.face(mat,vertices)

    def prism(self,name,mat,outline_xy,base,top):
        xy=list(map(tuple,outline_xy))
        if xy[0]==xy[-1]:xy.pop()
        if sum(xy[i-1][0]*p[1]-p[0]*xy[i-1][1] for i,p in enumerate(xy))<0:xy.reverse()
        for i,p in enumerate(xy):
            q=xy[(i+1)%len(xy)]
            self.face(mat,[(*p,base),(*q,base),(*q,top),(*p,top)])
        for tri in footprint_tris(xy):
            self.face(mat,[(*xy[i],top) for i in tri])
            self.face(mat,[(*xy[i],base) for i in tri[::-1]])

    def box(self,name,mat,center,size,angle=0):
        x,y,z=center
        if self.section == "CB10_AC":
            mat = finishes.pane_material(self, name, mat)
        if min(size)<=0:raise ValueError((name,size))
        xy=rectangle(x,y,size[0],size[1],angle)
        a=[(*p,z-size[2]/2) for p in xy];b=[(*p,z+size[2]/2) for p in xy]
        self.face(mat,a[::-1]);self.face(mat,b)
        for i in range(4):
            j=(i+1)%4
            points = [a[i],a[j],b[j],b[i]]
            uv = finishes.pane_uv(points, mat, center) if mat in finishes.WINDOWS else None
            self.face(mat,points,uv)

    def beam(self,name,mat,point1,point2,width,height=None):
        p,q=np.array(point1,dtype=float),np.array(point2,dtype=float)
        d=q-p
        if np.linalg.norm(d)<1e-8:return
        d/=np.linalg.norm(d)
        u=np.cross(d,[0,0,1] if abs(d[2])<.99 else [0,1,0])
        u/=np.linalg.norm(u)
        v=np.cross(d,u)*(height or width)/2;u=u*width/2
        a=[p-u-v,p+u-v,p+u+v,p-u+v];b=[pt+q-p for pt in a]
        self.face(mat,a[::-1]);self.face(mat,b)
        for i in range(4):
            j=(i+1)%4
            self.face(mat,[a[i],a[j],b[j],b[i]])

    def sign(self,name,text,center,width,height,facing,color="#e6d6b0"):
        key="sign_"+text+"_"+color.lstrip("#")
        if key not in self.textures:
            vertical=height>width*1.2 and "\n" not in text
            label="\n".join(text) if vertical else text
            fonts=[CAMPUS/"godot/assets/fonts/NotoSansSC-Regular.otf", Path("C:/Windows/Fonts/msyhbd.ttc"),Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")]
            path=next(f for f in fonts if f.exists())
            font=ImageFont.truetype(str(path),92)
            tmp=ImageDraw.Draw(Image.new("L",(1,1)))
            l,t,r,b=tmp.multiline_textbbox((0,0),label,font=font,spacing=5,align="center")
            canvas=Image.new("RGBA",(math.ceil(r-l+12),math.ceil(b-t+12)),(0,0,0,0))
            ImageDraw.Draw(canvas).multiline_text((6-l,6-t),label,font=font,fill=color,align="center",spacing=5)
            self.textures[key]=canvas;self.material(key,"#ffffff");self.image_for[key]=key
            self.materials[key]["alphaMode"]="MASK";self.materials[key]["alphaCutoff"]=.38
        self._sign_face(key,center,width,height,facing)

    def image_sign(self,name,png_path,center,width,height,facing):
        key="decal_"+name
        if key not in self.textures:
            self.textures[key]=Image.open(png_path).convert("RGBA")
            self.material(key,"#ffffff");self.image_for[key]=key
            self.materials[key]["alphaMode"]="MASK";self.materials[key]["alphaCutoff"]=.38
        self._sign_face(key,center,width,height,facing)

    def _sign_face(self,key,center,width,height,facing):
        outward={"east":(1,0),"west":(-1,0),"south":(0,1),"north":(0,-1)}[facing]
        right=np.array([-outward[1],outward[0],0])*(-width/2)
        mid=np.array(center);up=np.array([0,0,height/2])
        # Clockwise in east/south/up space seen from the facade; outward face for culling.
        self.face(key,[mid-right-up,mid-right+up,mid+right+up,mid+right-up],[(0,1),(0,0),(1,0),(1,1)])

    def solid(self,outline_xy,bottom,top):
        self.solids.append({"outline":[[round(float(v),4) for v in p] for p in outline_xy],
                            "bottom":round(bottom,4),"top":round(top,4)})

    def solid_box(self,center,size,angle=0):
        x,y,z=center;w,d,h=size
        self.solid(rectangle(x,y,w,d,angle),z-h/2,z+h/2)

    def save(self,path,single_mesh=False):
        used=list(dict.fromkeys(mat for _,mat in self.parts))
        doc={"asset":{"version":"2.0","generator":"USTC connected buildings photo model"},"scene":0,"scenes":[{"nodes":[]}],"nodes":[],"meshes":[],
             "materials":[self.materials[key] for key in used],"textures":[],"images":[],"bufferViews":[],"accessors":[]}
        binary=bytearray()
        def view(data,target=None):
            while len(binary)%4:binary.append(0)
            rec={"buffer":0,"byteOffset":len(binary),"byteLength":len(data)}
            if target:rec["target"]=target
            doc["bufferViews"].append(rec);binary.extend(data)
            return len(doc["bufferViews"])-1
        def acc(values,dtype,ct,typ,target):
            arr=np.asarray(values,dtype=dtype)
            rec={"bufferView":view(arr.tobytes(),target),"count":len(arr),"type":typ,"componentType":ct}
            if typ=="VEC3":
                rec.update(min=arr.min(axis=0).tolist(),max=arr.max(axis=0).tolist())
            doc["accessors"].append(rec);return len(doc["accessors"])-1
        textures={}
        def texture_index(key):
            if key not in textures:
                bio=io.BytesIO()
                if key in self.jpeg_images:
                    self.textures[key].save(bio,format="JPEG",quality=90,subsampling=0)
                    mime = "image/jpeg"
                else:
                    self.textures[key].save(bio,format="PNG")
                    mime = "image/png"
                idx=len(doc["images"])
                doc["images"].append({"name":key,"bufferView":view(bio.getvalue()),"mimeType":mime})
                textures[key]=idx
                doc["textures"].append({"source":idx})
            return textures[key]

        for mat in used:
            if mat in self.image_for:
                idx=texture_index(self.image_for[mat])
                self.materials[mat]["pbrMetallicRoughness"]["baseColorTexture"]={"index":idx}
            if mat in self.normal_for:
                key,scale=self.normal_for[mat]
                self.materials[mat]["normalTexture"]={"index":texture_index(key),"scale":scale}
        for (section,mat),(p,n,uv,ix) in self.parts.items():
            i=len(doc["nodes"]);name=section+"_"+mat.replace("\n","")
            doc["meshes"].append({"name":name,"primitives":[{"attributes":{"POSITION":acc(p,"<f4",5126,"VEC3",34962),"NORMAL":acc(n,"<f4",5126,"VEC3",34962),"TEXCOORD_0":acc(uv,"<f4",5126,"VEC2",34962)},"indices":acc(ix,"<u4",5125,"SCALAR",34963),"material":used.index(mat)}]})
            doc["nodes"].append({"name":name,"mesh":i});doc["scenes"][0]["nodes"].append(i)
        if single_mesh:
            primitives=[primitive for mesh in doc["meshes"] for primitive in mesh["primitives"]]
            doc["meshes"]=[{"name":self.section,"primitives":primitives}]
            doc["nodes"]=[{"name":self.section,"mesh":0}]
            doc["scenes"][0]["nodes"]=[0]
        while len(binary)%4:binary.append(0)
        doc["buffers"]=[{"byteLength":len(binary)}]
        js=json.dumps(doc,ensure_ascii=False,separators=(",",":")).encode();js+=b" "*(-len(js)%4)
        path.write_bytes(struct.pack("<4sII",b"glTF",2,28+len(js)+len(binary))+struct.pack("<I4s",len(js),b"JSON")+js+struct.pack("<I4s",len(binary),b"BIN\0")+binary)


def glazed_bridge(m):
    """Two-storey glazed A–B link; crossing at pavement level remains open."""
    from complex_details import east_forecourt, passage, roofs, west_link
    x0,x1=-295.8,-288.1
    y0,y1=529.5,541.55
    cx,cy=(x0+x1)/2,(y0+y1)/2
    w,d=x1-x0,y1-y0
    m.material("bridge_glass","#889ca1",.19,.24)
    m.material("bridge_reflection","#95a9ac",.22,.25)
    for key in ("bridge_glass","bridge_reflection"):
        m.materials[key]["alphaMode"]="BLEND"
        m.materials[key]["pbrMetallicRoughness"]["baseColorFactor"][3]=.63
    roofs(m)
    passage(m)
    west_link(m)
    east_forecourt(m)
    m.material("soffit","#807c70",.85)
    for z,thick,mat in [(4.28,.36,"soffit"),(7.95,.18,"concrete"),(11.54,.26,"metal")]:
        m.box("deck",mat,(cx,cy,z),(w,d,thick))
    for x in (x0+.14,x1-.14):
        m.box("edge_beam","metal",(x,cy,4.33),(.32,d,.45))
        for row,(lo,hi) in enumerate([(4.51,7.87),(8.04,11.39)]):
            for j in range(7):
                pitch=d/7;y=y0+(j+.5)*pitch
                mat="bridge_reflection" if (j+row)%4==0 else "bridge_glass"
                m.box("vision_panel",mat,(x,y,(lo+hi)/2),(.10,pitch-.06,hi-lo))
            for j in range(8):
                m.box("curtain_mullion","metal",(x,y0+j*d/7,(lo+hi)/2),(.17,.056,hi-lo))
        for z in (4.54,6.95,7.95,10.46,11.38):
            m.box("transom","metal",(x,cy,z),(.17,d,.064))
    for x in (x0+.23,cx,x1-.23):
        m.box("underside_crossbeam","concrete",(x,cy,4.025),(.30,d-.34,.24))
    m.solid_box((cx,cy,(3.92+11.67)/2),(w,d,11.67-3.92))
    for y in (y0+.5,y1-.5):
        m.box("brick_end_return","brick",(cx,y,7.96),(w-.7,.28,6.68))
        for h in (5.6,9.15):
            m.box("corridor_door","wood",(cx-.65,y+(.16 if y<cy else -.16),h),(1.65,.08,2.18))
    # East-facing photograph of the passage: a series of crossbeams recedes
    # westwards, with the vehicle and pedestrian lane open between the rows.
    start,end=-323.8,x0
    m.box("covered_walk","soffit",((start+end)/2,cy,4.42),(end-start,5.8,.32))
    m.solid_box(((start+end)/2,cy,4.42),(end-start,5.8,.32))
    for x in np.linspace(start+.35,end-.35,7):
        m.box("crossbeam","concrete",(x,cy,4.03),(.43,5.90,.44))
        for y in (cy-2.68,cy+2.68):
            m.box("colonnade","concrete",(x,y,2.01),(.51,.50,4.02))
            m.solid_box((x,y,2.01),(.51,.50,4.02))
    m.material("lane_asphalt","#50535a",.94)
    def paved_lane(name,outline):
        m.prism(name,"lane_asphalt",outline,-.025,.028)
        m.solid(outline,-.25,.028)
    paved_lane("underpass_paving",[(-325,529.79),(-282.5,529.79),(-282.5,541.14),(-325,541.14)])
    paved_lane("east_drive",[(-287.29,496.1),(-282.5,496.1),(-282.5,529.79),(-287.29,529.79)])
    north_forecourt(m)


def north_forecourt(m, north_annex=False):
    outline = [(-326.8,497.8),(-322.6,493.7),(-291,493.7),(-282.5,496.1)]
    if north_annex:
        # Retain the driveway across the north entrance. Its southern edge
        # follows the new rounded wing with a clear approach to the steps.
        outline.extend([(-282.5,502.25),(-301.9,502.25),(-301.9,512.18)])
    else:
        outline.extend([(-287.29,496.1),(-287.29,512.18),(-296.39,512.18)])
    outline.extend([(-321.62,512.18),(-326.8,508.2)])
    m.material("lane_asphalt","#50535a",.94)
    m.prism("north_forecourt","lane_asphalt",outline,-.025,.028)
    m.solid(outline,-.25,.028)
    # Rounded planting bed sits in the northwest recess beside the service entry.
    bed=[(-315.45,508.48),(-315.6,505.75),(-315.42,504.9),(-314.9,504.57),(-312.85,504.7),(-312.05,505.22),(-311.79,506.0),(-311.79,508.48)]
    m.prism("north_kerb","stone",bed,.029,.16)
    if north_annex:
        m.solid(bed,.028,.19)
    bx,by=-313.7,506.6
    m.material("ground_cover","#52653a",.93)
    m.prism("north_planting","ground_cover",[(bx+(x-bx)*.93,by+(y-by)*.91) for x,y in bed],.16,.22)
    for mat,col in (("maple_inner","#626148"),("maple_outer","#885544"),("maple_tips","#98674c")):
        m.material(mat,col,.93)
    # The short maple is rooted in the kerbed bed west of the door.
    m.beam("trunk","wood",(bx,by,.19),(bx+.13,by,2.33),.115)
    rng=np.random.default_rng(501)
    for j in range(12):
        a=j*2.4;r=.24+.70*np.sqrt(j/12)
        px,py=bx+r*math.cos(a),by+r*.83*math.sin(a)
        h=2.75-.70*r+rng.uniform(-.14,.14)
        m.beam("branch","wood",(bx,by,1.1),(px,py,h-.13),.055)
        rings=[]
        for dz,rad in ((-.46,.18),(-.12,.56),(.17,.43),(.39,.12)):
            rings.append([(px+(rad+rng.uniform(-.07,.07))*math.cos(k*math.tau/9+a),
                           py+(rad+rng.uniform(-.06,.06))*math.sin(k*math.tau/9+a),h+dz) for k in range(9)])
        for lo,hi in zip(rings,rings[1:]):
            for k in range(9):
                q=(k+1)%9
                m.face(("maple_inner","maple_outer","maple_tips")[(k+j//3)%3],[lo[k],lo[q],hi[q],hi[k]])
        m.face("maple_tips",rings[-1])


if __name__=="__main__":
    from sports import build as sports
    from humanities import build as humanities
    m=Model()
    for section,build in [("CB05_B",sports),("CB10_AC",humanities),("AB_Link",glazed_bridge)]:
        m.section=section;build(m)
    OUTPUT.mkdir(parents=True,exist_ok=True)
    m.save(OUTPUT/"pe_humanities.glb")
    (OUTPUT/"pe_humanities_collision.json").write_text(json.dumps({
        "solids":m.solids, "parking":m.parking, "planting":m.planting
    },separators=(",",":")),encoding="utf8")
    print(f"{len(m.parts)} mesh batches, {sum(len(i[3])//3 for i in m.parts.values())} triangles, {len(m.solids)} colliders")
    # Beyond close viewing distance a shared silhouette replaces the detailed vehicle.
    from complex_details import parked_scooter
    m.parts.clear()
    m.section = "Distant"
    m.material("mint", "#91beb3", .32, .16)
    m.material("cream", "#ead9bc", .38, .11)
    parked_scooter(m, *ORIGIN, math.pi, "mint")
    for v in (-.151,.151):
        for a,b in [((-.80,v,.90),(-.48,v,.90)),((-.80,v,.90),(-.73,v,.68)),
                    ((-.73,v,.68),(-.47,v,.68)),((-.47,v,.68),(-.48,v,.90))]:
            m.beam("basket","metal",(ORIGIN[0]+a[0],ORIGIN[1]+a[1],a[2]),(ORIGIN[0]+b[0],ORIGIN[1]+b[1],b[2]),.022)
    for u in (-.80,-.48):
        m.box("basket rail","metal",(ORIGIN[0]+u,ORIGIN[1],.90),(.025,.33,.024))
    m.box("luggage rack","steel",(ORIGIN[0]+.74,ORIGIN[1],.72),(.22,.23,.032))
    m.box("rear lamp","red",(ORIGIN[0]+.765,ORIGIN[1],.58),(.06,.18,.10))
    m.save(OUTPUT/"campus_scooter_distant.glb",single_mesh=True)
