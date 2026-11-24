import numpy as np, json, struct
from pathlib import Path
from math import pi
def blend(a,b,k):
 h=np.maximum(k-np.abs(a-b),0)/k
 return np.minimum(a,b)-h*h*k*.25
def ell(p,c,r):
 q=(p-np.array(c))/np.array(r)
 return (np.linalg.norm(q,axis=-1)-1)*min(r)
def path(t,controls):
 pts=np.array(controls);t=t[:,None]
 return (1-t)**3*pts[0]+3*t*(1-t)**2*pts[1]+3*t*t*(1-t)*pts[2]+t**3*pts[3]
def tube(pts,radii,n=10):
 rings=[]
 for i,p in enumerate(pts):
  d=pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)];d=d/np.linalg.norm(d)
  u=np.cross(d,[0,1,0] if abs(d[1])<.91 else [0,0,1]);u/=np.linalg.norm(u)
  v=np.cross(d,u);a=np.arange(n)*2*pi/n
  rings.append(p+radii[i]*(np.cos(a)[:,None]*u+np.sin(a)[:,None]*v))
 idx=[]
 for i in range(len(pts)-1):
  for j in range(n):
   a=i*n+j;b=i*n+(j+1)%n;idx.extend([[a,b,b+n],[a,b+n,a+n]])
 return np.vstack(rings),np.array(idx)
def main(cal):
 h=np.array([-.040,.125,-.119] if cal else [0,.167,-.146])
 def head(p):
  q=p-h
  d=ell(q,[0,.007,0],[.090,.076,.074])
  for side in [-1,1]:
   d=blend(d,ell(q,[side*.046,-.012,-.021],[.045,.041,.047]),.016)
   d=blend(d,ell(q,[side*.017,-.018,-.054],[.030,.024,.025]),.021)
   # Tapered pinnae, broad roots and slightly rounded tips.
   t=np.clip((q[...,1]-.033)/.082,0,1)
   rx=.035*(1-.91*t);rz=.025*(1-.88*t)
   xx=q[...,0]-side*(.049+.021*t);zz=q[...,2]-(.007+.010*t)
   ear=(np.sqrt((xx/rx)**2+(zz/rz)**2)-1)*rz
   ear=np.maximum(ear,np.maximum(.033-q[...,1],q[...,1]-.115))
   d=blend(d,ear,.012)
  return d
 def body(p):
  d=ell(p,[.017 if cal else 0,.098,.047],[.145 if cal else .12,.106,.173 if cal else .189])
  d=blend(d,ell(p,[.058 if cal else .0,.101,.123],[.119,.112,.123]),.025)
  d=blend(d,ell(p,[h[0]*.65,.112,-.080],[.096,.098,.10]),.03)
  for sign in [-1,1]:
   d=blend(d,ell(p,[h[0]+sign*.046,.032,-.151-(.03 if cal and sign<0 else 0)],[.032,.028,.056]),.012)
  return np.maximum(blend(d,head(p),.012),-.002-p[...,1])
 # A narrow band around the zero surface is meshed at 3 mm.
 axes=[np.arange(a,b,.0032) for a,b in [(-.24,.26),(-.01,.32),(-.30,.30)]]
 grid=np.stack(np.meshgrid(*axes,indexing='ij'),-1)
 f=body(grid)
 offs=np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]])
 corners=np.stack([f[i:i+len(axes[0])-1,j:j+len(axes[1])-1,k:k+len(axes[2])-1] for i,j,k in offs],-1)
 cells=np.argwhere((corners.min(-1)<=0)&(corners.max(-1)>0))
 ids=np.ravel_multi_index((cells[:,None,:]+offs).transpose(2,0,1),f.shape)
 flat=f.ravel();verts=[];faces=[];offset=0
 for tet in [[0,1,2,6],[0,2,3,6],[0,3,7,6],[0,7,4,6],[0,4,5,6],[0,5,1,6]]:
  t=ids[:,tet];signs=flat[t]<0
  for case in range(1,15):
   bits=np.array([(case>>k)&1 for k in range(4)],bool)
   ts=t[np.all(signs==bits,axis=1)]
   if not len(ts):continue
   inside=np.flatnonzero(bits);outside=np.flatnonzero(~bits)
   pairs=[(a,b) for a in inside for b in outside]
   if len(pairs)==4:pairs=[pairs[i] for i in (0,1,3,2)]
   rings=[]
   for a,b in pairs:
    u,v=ts[:,a],ts[:,b];k=flat[u]/(flat[u]-flat[v]);g=grid.reshape(-1,3)
    rings.append(g[u]+(g[v]-g[u])*k[:,None])
   points=np.stack(rings,1);n=len(pairs);idx=np.arange(len(ts))*n+offset
   faces.append(idx[:,None]+[0,1,2])
   if n==4:faces.append(idx[:,None]+[0,2,3])
   verts.append(points.reshape(-1,3));offset+=points.size//3
 v,inv=np.unique(np.round(np.vstack(verts),6),axis=0,return_inverse=True);idx=inv[np.vstack(faces)]
 norm=np.stack([(body(v+e*.0006)-body(v-e*.0006)) for e in np.eye(3)],1)
 norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1.e-8)
 wrong=(np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]])*norm[idx[:,0]]).sum(1)<0;idx[wrong]=idx[wrong][:,[0,2,1]]
 def colors(v):
  x,y,z=v.T
  if not cal:
   mix=np.clip(y/.26,0,1)[:,None];return np.array([.018,.019,.024])+mix*np.array([.024,.024,.028])
  def mark(cx,cz,rx,rz):
   d=((x-cx)/rx)**2+((z-cz)/rz)**2+.11*np.sin(59*z+38*x)
   return np.clip((1-d)*10,0,1)[:,None]
  orange=np.maximum(mark(-.081,-.102,.081,.087),mark(.073,.013,.12,.123))
  black=np.maximum(mark(.007,-.129,.037,.058),mark(-.081,.108,.106,.082))
  cream=np.tile([.81,.74,.62],(len(x),1))
  c=cream*(1-orange)+np.array([.49,.162,.048])*orange
  return c*(1-black)+np.array([.030,.025,.023])*black
 meshes=[(v,idx,norm,colors(v))]
 def add(v,i,c):
  n=np.zeros_like(v);tn=np.cross(v[i[:,1]]-v[i[:,0]],v[i[:,2]]-v[i[:,0]])
  for col in i.T:np.add.at(n,col,tn)
  n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-14)
  meshes.append((v,i,n,np.tile(c,(len(v),1)) if np.ndim(c)==1 else c))
 def stroke(pts,r,c):
  v,i=tube(pts,r);add(v,i,c)
 t=np.linspace(0,1,44)
 ctr=([[.105,.091,.16],[.256,.063,.086],[.19,.032,-.186],[-.027,.036,-.193]] if cal else [[-.075,.085,.175],[-.195,.052,.13],[-.155,.033,-.041],[-.089,.040,-.112]])
 pts=path(t,ctr);v,i=tube(pts,.034*(1-.83*t**2),16);add(v,i,colors(v))
 def surface(x,y):
  lo=np.full_like(x,-.13);hi=np.full_like(x,-.015)
  for _ in range(15):
   mid=(lo+hi)*.5;outside=head(np.stack((x,y,mid),1)+h)>0
   lo=np.where(outside,mid,lo);hi=np.where(outside,hi,mid)
  return lo
 for side in [-1,1]:
  # A sleepy lid follows the actual curvature of the cheek.
  t=np.linspace(0,1,22);x=side*(.015+.044*t);y=.001+.006*np.sin(pi*t)+.010*t
  stroke(np.stack((x,y,surface(x,y)-.0015),1)+h,.0006+.0018*np.sin(pi*t),[.009,.008,.011])
  # Inner ear membrane follows the tapered shell.
  pts=[];tri=[]
  for j in range(11):
   u=j/10;yy=.050+.052*u;f=(yy-.033)/.082;cx=side*(.049+.021*f)
   for k in range(7):
    a=(k/3-1)*(.57*(1-u)+.13)*np.sin(.28+2.65*u)
    xx=cx+a*.035*(1-.91*f);zz=.007+.010*f-.025*(1-.88*f)*np.sqrt(1-a*a)-.00085
    pts.append(h+[xx,yy,zz])
    if j and k:
     ix=j*7+k;tri.extend([[ix-8,ix,ix-7],[ix-8,ix-1,ix]])
  add(np.array(pts),np.array(tri),[.31,.145,.13] if cal else [.12,.066,.073])
  for j in range(3):
   t=np.linspace(0,1,15);x=side*(.027+.055*t);y=-.023+.004*j-.010*t*t+.005*j*t
   z=surface(x[:1],y[:1])[0]-.002-.012*t
   stroke(np.stack((x,y,z),1)+h,.00050*(1-.82*t),[.32,.29,.26])
 # A single small, tapered nose with a restrained philtrum.
 v=np.array([[-.010,-.012,-.081],[.010,-.012,-.081],[0,-.022,-.082],[0,-.015,-.086]])+h
 add(v,np.array([[0,1,3],[1,2,3],[2,0,3],[0,2,1]]),[.32,.143,.136] if cal else [.067,.052,.063])
 # Single draw surface with vertex pigmentation across the sculpt.
 buf=bytearray();views=[];acc=[]
 def put(arr,typ,ct):
  data=arr.tobytes();j=len(views);views.append(dict(buffer=0,byteOffset=len(buf),byteLength=len(data)));buf.extend(data);buf.extend(bytes(-len(buf)%4))
  a=dict(bufferView=j,componentType=ct,count=len(arr),type=typ)
  if typ=='VEC3':a.update(min=arr.min(0).tolist(),max=arr.max(0).tolist())
  acc.append(a);return len(acc)-1
 off=0;idx=[]
 for v,i,n,c in meshes:idx.append(i+off);off+=len(v)
 attrs={name:put(np.vstack([m[col] for m in meshes]).astype('<f4'),'VEC3',5126) for name,col in [('POSITION',0),('NORMAL',2),('COLOR_0',3)]}
 prim=dict(attributes=attrs,indices=put(np.vstack(idx).ravel().astype('<u4'),'SCALAR',5125),material=0)
 g=dict(asset=dict(version='2.0'),scene=0,scenes=[dict(nodes=[0])],nodes=[dict(mesh=0,name='RestingKitten')],meshes=[dict(primitives=[prim])],materials=[dict(doubleSided=True,pbrMetallicRoughness=dict(metallicFactor=0,roughnessFactor=.89))],bufferViews=views,accessors=acc,buffers=[dict(byteLength=len(buf))])
 doc=json.dumps(g).encode();doc+=b' '*(-len(doc)%4)
 Path('curled_calico.glb' if cal else 'black_loaf.glb').write_bytes(struct.pack('<4sIIII',b'glTF',2,28+len(doc)+len(buf),len(doc),0x4e4f534a)+doc+struct.pack('<II',len(buf),0x004e4942)+buf)
for cal in [False,True]:main(cal)
