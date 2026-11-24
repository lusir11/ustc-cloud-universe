import numpy as np, struct,zlib
from pathlib import Path
w,h=1774,887
lon=(np.arange(w)+.5)*2*np.pi/w
elev=(.5-(np.arange(h)+.5)/h)*np.pi
# Project onto a horizontal cloud layer; no seam or distortion at the zenith.
s=np.maximum(.32,np.sin(elev))[:,None]
x=np.cos(elev)[:,None]*np.cos(lon)/s
y=np.cos(elev)[:,None]*np.sin(lon)/s
rng=np.random.default_rng(821)
density=np.zeros_like(x)
for cx,cy,length,width,angle,bend in [(-.13,.16,.65,.10,.43,.22),(.57,-.25,.41,.075,.66,-.18),(-.73,-.57,.48,.095,.38,.21)]:
 u=(x-cx)*np.cos(angle)+(y-cy)*np.sin(angle)
 v=-(x-cx)*np.sin(angle)+(y-cy)*np.cos(angle)
 for j in range(49):
  offset=rng.normal(0,width*.46)
  center=rng.normal(0,length*.25)
  scale=length*rng.uniform(.45,1.12)
  t=(u-center)/scale
  ridge=offset*(1+.35*np.sin(2*t))+bend*(u*u)+.032*np.sin(u*7+offset*19)+.013*np.sin(u*17+offset*40)+rng.normal(0,.019)*u
  thickness=rng.uniform(.003,.010)*(1.2+.30*np.cos(3*t))
  density+=rng.uniform(.04,.13)*np.exp(-t*t*1.8-((v-ridge)/thickness)**2)
alpha=(1-np.exp(-density))*.65*np.clip((elev[:,None]-.56)/.23,0,1)
rgba=np.empty((h,w,4),np.uint8);rgba[:,:,:3]=[231,240,247];rgba[:,:,3]=np.rint(alpha*255)
def chunk(k,b):return struct.pack('!I',len(b))+k+b+struct.pack('!I',zlib.crc32(k+b))
Path('wisps.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+r.tobytes() for r in rgba)))+chunk(b'IEND',b''))
