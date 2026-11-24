from pathlib import Path
import json,struct
import numpy as np
from zipfile import ZipFile
assets=Path('F:/cloudUSTC/cloudUSTC-lusir11/campus/godot/assets')
folder=Path('forms');folder.mkdir(exist_ok=True)
for family,sources,height in [('cedar',['tree_conifer'],14),('plane',['tree_plane_a','tree_plane_b','tree_plane_c'],15),('grove',['study_canopy_0','study_canopy_1','study_canopy_2'],10)]:
 for k in range(10):
  source=sources[k%len(sources)]
  data=(assets/(source+'.glb')).read_bytes(); size=struct.unpack_from('<I',data,12)[0]
  gltf=json.loads(data[20:20+size]);buf=bytearray(data[28+size:])
  phase=k*2.39996
  def shape(points):
   x,y,z=points.T
   h=np.clip(y/height,0,1.3)
   a=np.arctan2(z,x)
   r=np.hypot(x,z)
   twist=(.48*np.sin(phase+1.3))*h
   spread=1+(r/(1+r))*(.32*np.cos(2*a+phase)+.22*np.sin(3*a-phase))+.24*np.cos(phase)*h
   bent_x=spread*(np.cos(twist)*x-np.sin(twist)*z)+height*h*h*.18*np.sin(phase)
   bent_z=spread*(np.sin(twist)*x+np.cos(twist)*z)+height*h*h*.14*np.cos(phase)
   lift=(.19*np.sin(a+phase)+.10*np.sin(h*9+phase))*r*np.clip(y/2.,0,1)
   # Width, depth, crown height, top compression, twin leaders and directional loss.
   profiles=[(1.60,1.25,.72,.47,.0,.05),(.64,.82,1.36,0.,.0,.12),
             (1.49,.76,.90,.18,.55,.30),(.86,1.1,1.17,.03,.06,.50),
             (1.32,1.18,1.,.10,.74,.13),(1.17,1.47,.80,.37,.08,.12),
             (.73,.76,1.24,.20,.30,.26),(1.38,.98,1.09,.04,.29,.56),
             (1.24,1.36,.94,.30,.64,.23),(.96,.78,1.14,0.,.02,.55)]
   width,depth,crown_height,flat,split,loss=profiles[k]
   base=.27 if family=='cedar' else .42
   activation=np.clip((h-.06)/.31,0,1)
   activation=activation**2*(3-2*activation)
   u=np.maximum(h-base,0)/(1-base)
   side=np.cos(a-phase)*r/(r+.4)
   cut=1-loss*np.maximum(side,0)**2*activation
   bent_x*=1+activation*(width*cut-1)
   bent_z*=1+activation*(depth*cut-1)
   fork=np.cos(2*(a-phase))*r/(r+.65)
   crown=u*crown_height-flat*u*u*.70+split*.27*fork*u
   new_y=np.minimum(y,base*height)+height*(1-base)*crown+lift
   return np.stack((bent_x,new_y,bent_z),axis=1)
  def array(i):
   a=gltf['accessors'][i];v=gltf['bufferViews'][a['bufferView']]
   return np.ndarray((a['count'],3),'<f4',buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',12),4))
  done=set()
  for mesh in gltf['meshes']:
   for primitive in mesh['primitives']:
    ids=primitive['attributes'];i=ids['POSITION']
    if i in done:continue
    done.add(i);arr=array(i);original=arr.astype(float);normal=array(ids['NORMAL'])
    mapped=shape(original)
    jac=np.stack([(shape(original+v*.001)-shape(original-v*.001))/.002 for v in np.eye(3)],axis=2)
    n=np.linalg.solve(jac.transpose(0,2,1),normal[:,:,None])[:,:,0]
    normal[:]=n/np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-8)
    arr[:]=mapped
    gltf['accessors'][i].update(min=arr.min(0).tolist(),max=arr.max(0).tolist())
  doc=json.dumps(gltf,separators=(',',':')).encode();doc+=b' '*(-len(doc)%4)
  (folder/(f'{family}_{k}.glb')).write_bytes(struct.pack('<4sIIII',b'glTF',2,28+len(doc)+len(buf),len(doc),0x4e4f534a)+doc+struct.pack('<II',len(buf),0x004e4942)+buf)

