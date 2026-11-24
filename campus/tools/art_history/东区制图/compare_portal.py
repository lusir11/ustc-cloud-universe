from pathlib import Path
import csv, math, json, html
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
D=Path(__file__).resolve().parent
O=D/'官方地图核对'; O.mkdir(exist_ok=True)
# Coordinates read at the 840x1100 (model) and 960x800 (portal mosaic) review scales.
rows=[
('C1','配准','田径场足球中圈中心',(207.0,612.0),(330.2,334.2)),
('C2','配准','行政楼与校史馆间庭园圆心',(493.0,629.0),(509.2,389.5)),
('C3','配准','眼镜湖中轴南端与一教北侧横路交口',(410.5,291.5),(553.0,239.5)),
('C4','配准','南部球场以东，南北路与宽横路交口',(365.0,810.0),(373.0,442.5)),
('V1','留出','郭沫若广场南段纪念物基座中心（植被遮挡，近似）',(422.8,458.0),(511.8,312.3)),
('V2','留出','图书馆南门前中轴与横路交口（树冠遮挡，近似）',(434.4,579.0),(482.5,359.0)),
('V3','留出','南部四片蓝色网球场中西北一片的场心',(278.5,746.0),(339.3,400.8)),
('V4','留出','C4 以东下一处南北路与宽横路交口（按路口中心估读）',(453.2,806.5),(431.0,453.3))]
M=np.array([r[3] for r in rows]); R=np.array([r[4] for r in rows]); ctrl=[i for i,r in enumerate(rows) if r[1]=='配准']; chk=[i for i,r in enumerate(rows) if r[1]=='留出']
H=lambda p:np.column_stack([p,np.ones(len(p))])
# Least squares in model metres for interpretable independent check residuals.
B=np.linalg.lstsq(H(R[ctrl]),M[ctrl],rcond=None)[0]
P=H(R)@B
err=P-M
dist=np.linalg.norm(err,axis=1)
A=np.linalg.inv(np.vstack([B.T,[0,0,1]]))[:2,:]
model=Image.open(D/'东区模型正射底图.png').convert('RGB')
ref=Image.open(D/'东区官方参考全图.jpg').convert('RGB')
def font(sz):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',sz)
def make_rectified(modelsize):
 w,h=modelsize
 # Portal image pixels = 3.2 * portal review coordinates, output pixels per model metre = w/840.
 transform=A*3.2; transform[:,:2]/=w/840
 return ref.transform((w,h),Image.Transform.AFFINE,tuple(transform.flatten()),Image.Resampling.BICUBIC,fillcolor=(223,224,215))
scale=2
model=model.resize((840*scale,1100*scale),Image.Resampling.LANCZOS)
reg=make_rectified(model.size)
model.save(O/'模型.jpg',quality=94)
reg.save(O/'校图图面校正.jpg',quality=94)
ref.save(O/'官方原图.jpg',quality=92)
def mark(draw,xy,txt,color,unit=1):
 x,y=xy;r=unit*5
 draw.ellipse((x-r,y-r,x+r,y+r),outline='#101718',width=unit*4)
 draw.ellipse((x-r,y-r,x+r,y+r),outline=color,width=unit*2)
 draw.text((x+r+2,y-r-2),txt,font=font(11*unit),fill=color,stroke_width=2,stroke_fill='#101718')
board=Image.new('RGB',(1580,821),'#f4f2e9'); b=ImageDraw.Draw(board)
b.text((25,12),'科大东区  /  原模型与官方校园图',font=font(28),fill='#172a26')
b.text((25,56),'同名地面点按图人工选取。C 为配准点，V 为独立检查点。校图为斜视绘制，校正只适用于地面。',font=font(17),fill='#344a43')
cards=[(model,'原模型 · 正射'),(ref,'官方原图 · 斜视'),(Image.blend(model,reg,.50),'校正后 · 50% 叠加')]
for k,(im,title) in enumerate(cards):
 bx=22+k*520;b.text((bx,102),title,font=font(21),fill='#203731')
 if k==1:
  # Crop background and retain the entire East Campus.
  view=im.crop((300,375,2850,2040)); orig=np.array([300,375]); pts=(R*3.2-orig)
 else:
  view=im; pts=M*scale
 ratio=min(504/view.width,649/view.height); size=tuple(round(q*ratio) for q in view.size)
 x=bx+(504-size[0])//2;y=141+(649-size[1])//2
 board.paste(view.resize(size,Image.Resampling.LANCZOS),(x,y))
 for j,r in enumerate(rows):
  xy=pts[j]*ratio+[x,y];mark(b,xy,r[0],'#6aefb5' if j in ctrl else '#ffd472')
  if k==2 and j in chk:
   target=P[j]*scale*ratio+[x,y]; b.line((tuple(xy),tuple(target)),fill='#a72b52',width=2)
b.text((22,788),'校图来源  中国科学技术大学虚拟校园 map.ustc.edu.cn   ·   底图绘制日期未核实   ·   校外背景仅供定向',font=font(16),fill='#344a43')
board.save(O/'配准前后对照.jpg',quality=94)
with (O/'逐点图面差异.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.writer(f);wr.writerow(['编号','用途','地面特征','模型原PNG像素x','模型原PNG像素y','门户拼图原像素x','门户拼图原像素y','校正后减模型 向东(模型米)','向南(模型米)','图面残差(模型米)'])
 for i,r in enumerate(rows):wr.writerow([*r[:3],*(M[i]*4).round(2),*(R[i]*3.2).round(2),*err[i].round(2),round(dist[i],2)])
def rms(seq):return math.sqrt(np.mean(dist[seq]**2))
table=''.join('<tr><td>'+r[0]+'</td><td>'+r[2]+'</td><td>'+f'{dist[i]:.1f}'+'</td></tr>' for i,r in enumerate(rows))
dots=''.join(f'<i class="dot" style="left:{M[i,0]/840*100:.4f}%;top:{M[i,1]/1100*100:.4f}%">{r[0]}</i>' for i,r in enumerate(rows))
page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>东区地面布局核对</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f6f5ef;color:#192d29;font:16px/1.55 "Microsoft YaHei",sans-serif}main{max-width:1150px;margin:auto;padding:24px}h1{font-size:26px;margin:0}h2{font-size:20px}label{display:inline-flex;align-items:center;gap:7px;margin-right:20px}input[type=range]{width:185px}a{color:#156454}header{background:#f6f5ef;position:sticky;top:0;z-index:5;padding:10px 0}#scroller{height:70vh;overflow:auto;background:#e3e4dc}#map{width:min(100%,790px);position:relative}#map img{width:100%;display:block}#overlay,#dots{position:absolute;inset:0}#overlay{opacity:.5}.dot{position:absolute;transform:translate(-4px,-7px);font: bold 12px/14px sans-serif;color:#fede86;text-shadow:0 1px 3px black;background:#24312dcd;padding:1px 3px;border-left:2px solid white}table{border-collapse:collapse}td,th{padding:5px 14px 5px 0;text-align:left;border-bottom:1px solid #ccd5cc}</style><main>
<h1>科大东区地面布局核对</h1><p>拖动滑块切换同一范围内的模型与校图，放大后可滚动查看。查看建筑时比较与地面接触的位置。</p>
<header><label>校图占比 <input id="op" type="range" min="0" max="100" value="50"><output id="val">50%</output></label><label>放大 <select id="zoom"><option value="0">适应窗口</option><option>100%</option><option>200%</option></select></label><label><input id="pins" type="checkbox" checked>显示点号</label></header>
<div id="scroller"><div id="map"><img src="模型.jpg" alt="主游戏模型"><img id="overlay" src="校图图面校正.jpg" alt="按地面点校正的官方斜视图"><div id="dots">DOTS</div></div></div>
<p><a href="官方原图.jpg">查看未经配准的官方图层</a>　<a href="逐点图面差异.csv">逐点差异 CSV</a>　<a href="https://map.ustc.edu.cn/">中国科学技术大学虚拟校园</a></p>
<h2>配准与适用范围</h2><p>校图采用官方 zoom3 图块 x=12…23、y=3…12，左上为 12_3.jpg，256 像素每块。绘制日期及绝对控制精度未核实。以 C1–C4 对校图做二维仿射，使其地面尽量贴合模型；V1–V4 不参与拟合。两图各自的原像素坐标已保存在 CSV。模型原图采样 0.25 项目米/像素。官方图中高层屋顶有投影位移，树冠会遮住路口，手工选点也带有误差。所有数值均为模型平面上的两图差异，不能验证 WGS84 绝对位置或推导 Google Earth 的平移量。北端、南端及东侧住宅区离这些控制点较远，外推只能作目视参考。</p><p>STAT</p><table><tr><th>点号</th><th>位置</th><th>图面差异（模型米）</th></tr>TABLE</table>
<script>const get=id=>document.getElementById(id);get('op').oninput=e=>{get('overlay').style.opacity=e.target.value/100;get('val').textContent=e.target.value+'%'};get('zoom').onchange=e=>get('map').style.width=({'0':'min(100%,790px)','100%':'1680px','200%':'3360px'})[e.target.value];get('pins').onchange=e=>get('dots').hidden=!e.target.checked;</script></main>'''
stat=f'配准点 RMS {rms(ctrl):.1f} 模型米；留出检查点 RMS {rms(chk):.1f} 模型米，单点范围 {dist[chk].min():.1f}–{dist[chk].max():.1f} 模型米。RMS 为均方根差。'
(O/'打开对照.html').write_text(page.replace('DOTS',dots).replace('STAT',stat).replace('TABLE',table),encoding='utf-8')
print(stat)
for i,r in enumerate(rows):print(r[0],r[2],round(dist[i],2))
