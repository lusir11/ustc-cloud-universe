import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

base = Path(__file__).resolve().parent
out = base / '东区开发分区'
out.mkdir(exist_ok=True)
campus = Path('F:/cloudUSTC/cloudUSTC-lusir11/campus')
geo = json.loads((campus / 'renders/coverage/coverage.json').read_text('utf-8'))
angle = geo['coordinates']['south_rotation_radians']
c, s = math.cos(angle), math.sin(angle)
S = 3
W, H = 840, 1100
size = (W*S, H*S)
def xy(x,z):
    return (round((400+x*c+z*s)*S), round((140-x*s+z*c)*S))
with Image.open(base / '东区模型正射底图.png') as source:
    assert source.size == (W*4, H*4), 'Unexpected Godot capture dimensions'
    model = source.convert('RGB').resize(size,Image.Resampling.LANCZOS)

# Local axes in metres. Shared cuts use the teaching, sports and research road network.
zmap = Image.new('L', size, 3)
d = ImageDraw.Draw(zmap)
def zone(n,points):
    d.polygon([xy(*p) for p in points], fill=n)
zone(8,[(99,-200),(900,-200),(900,1200),(128,670),(150,510),(185,446),(186,356),(174,228),(75,233),(98,23)])
zone(2,[(99,-200),(900,-200),(900,55),(94,55),(98,23)])
zone(1,[(-800,-200),(99,-200),(98,23),(75,233),(-79,232),(-194,247),(-800,260)])
zone(4,[(-79,337),(74,338),(75,233),(174,228),(186,356),(185,446),(-79,441)])
zone(5,[(-800,348),(-220,348),(-165,352),(-165,384),(-79,399),(-81,542),(-271,550),(-800,550)])
zone(6,[(-800,550),(-271,550),(-81,542),(-82,665),(-175,667),(-385,663),(-800,660)])
zone(7,[(-79,441),(185,446),(173,540),(150,620),(128,670),(-82,665)])
south_cut=[(-800,660),(-385,663),(-175,667),(-82,665),(20,668),(128,670),(900,680)]
zone(9,south_cut+[(900,1200),(-800,1200)])
zone(10,[(20,668),(128,670),(900,680),(900,1200),(-44,1200),(-44,862),(-52,753),(18,753)])
mask=Image.new('L',size)
ImageDraw.Draw(mask).polygon([xy(*p) for p in geo['campus_boundary_polygon']],fill=255)
zmap=Image.composite(zmap,Image.new('L',size),mask)
zones=[
('老北门 · 樱花大道 · 一教','首做样板','高','树种、湖岸、铺装与一教入口连续精做。','走一遍校门到教室，核对尺度与步行时长。','#ffb94a',(-8,103)),
('五教与北侧学院楼','入口近景','中','精做五教入口、楼牌和主要转角。','其余教学楼复用窗格、层高与立面构件。','#57cdec',(222,-10)),
('郭沫若广场与西侧连接区','地标近景','高','广场纪念物、林荫路和西侧入口定制。','从西侧进校园时，连续检查地标视线。','#f18c86',(-9,278)),
('新老图书馆 · 二教','入口近景','高','移植图书馆样景的幕墙、架空层和台阶。','用二教入口衔接楼层、教室活动的定位。','#aaafff',(36,393)),
('田径场与学生公寓','活动近景','中','校准跑道、球场、看台和出入口尺度。','公寓楼体复用，近路一侧补门牌和车棚。','#56d0ac',(-202,466)),
('南侧球场与公寓','沿路细化','中','复用球网、围栏、球场面层及公寓窗格。','重点处理场地边缘和出入口的步行碰撞。','#f4a16b',(-202,604)),
('行政楼 · 校史馆 · 中部庭院','地标近景','高','行政楼与校史馆分别做入口和识别立面。','保留庭院轴线，沿步行路线补校史导览。','#df9edb',(44,553)),
('东侧住宅与生活街巷','沿路细化','中','按住宅楼型成组复用，保留巷道疏密。','入口、车棚与生活节点做可辨识的差异。','#a4d675',(275,280)),
('礼堂与西南教学科研区','重点近景','较高','礼堂单独制作，门诊及院系楼按楼型分组。','采集入口与材料变化，背街先做体块。','#ecd570',(-202,756)),
('南部科研楼群与南缘','沿路细化','较高','按楼群整理体量、屋顶和沿路立面。','物质科学教研楼优先统一尺度与构件。','#72b8db',(117,813)),
]
palette=np.array([[0,0,0]]+[list(bytes.fromhex(z[5][1:])) for z in zones],dtype=np.uint8)
ids=np.asarray(zmap)
assert set(np.unique(ids))==set(range(11))
assert all(ids[xy(*z[6])[1],xy(*z[6])[0]]==i for i,z in enumerate(zones,1))
edges=(np.asarray(zmap.filter(ImageFilter.MaxFilter(5)))!=np.asarray(zmap.filter(ImageFilter.MinFilter(5))))
outline=np.asarray(Image.fromarray(edges).convert('L').filter(ImageFilter.MaxFilter(5)))>0
ink=np.zeros((*ids.shape,4),dtype=np.uint8)
ink[:,:,:3]=palette[ids]; ink[:,:,3]=np.where(ids>0,36,0)
ink[outline]=[39,49,52,210]
ink[edges]=[252,250,233,230]
overlay=Image.fromarray(ink)
od=ImageDraw.Draw(overlay)
def font(n,bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/msyh'+('bd' if bold else '')+'.ttc',round(n*S))
for i,(_,_,_,_,_,col,pos) in enumerate(zones,1):
    px,py=xy(*pos); r=16*S
    od.ellipse((px-r,py-r,px+r,py+r),fill='#14272c',outline=col,width=3*S)
    od.text((px,py-S),f'{i:02}',font=font(14,True),fill='white',anchor='mm')
model=Image.alpha_composite(model.convert('RGBA'),overlay).convert('RGB')

board=Image.new('RGB',(1280*S,1260*S),'#f5f4ee')
bd=ImageDraw.Draw(board)
def txt(x,y,text,sz,col='#172c30',bold=False):
    bd.text((round(x*S),round(y*S)),text,font=font(sz,bold),fill=col,anchor='lt')
def rect(a,b,c,d,color):
    bd.rectangle((a*S,b*S,c*S,d*S),fill=color)
txt(24,19,'中国科学技术大学东区',16,'#426760',True)
txt(22,44,'校园开发分区图',38,bold=True)
txt(310,61,'原项目模型俯视图   /   10 个制作区域',16,'#526660')
txt(1032,60,'东区建模分工   ·   讨论稿',15,'#526660')
mx,my=22,102
board.paste(model,(mx*S,my*S))
rect(36,116,94,152,'#203534');txt(45,124,'↑ 北',18,'#ffffff',True)
rect(35,1154,163,1188,'#203534')
txt(44,1158,'0',10,'white');txt(119,1158,'100 m',10,'white')
rect(45,1174,145,1178,'#faf9e9');rect(95,1174,144,1176,'#203534')
left=888
txt(left,105,'各区制作重点',24,bold=True)
txt(left,143,'细节按游玩距离分配，工作量综合考虑面积和资产复用。',13,'#526660')
for i,(name,detail,effort,l1,l2,col,_) in enumerate(zones,1):
    y=179+(i-1)*99
    rect(left,y+1,left+30,y+26,col)
    txt(left+4,y+4,f'{i:02}',15,'#172c30',True)
    txt(left+40,y,name,18,bold=True)
    txt(left+40,y+26,f'{detail}   /   工作量{effort}',13,'#3e6865',True)
    txt(left+1,y+48,l1,13);txt(left+1,y+69,l2,13)
    rect(left,y+91,1257,y+91,'#d2d9d2')
rect(22,1212,1257,1212,'#b6c2bb')
txt(23,1222,'底图来自原项目 Godot 东区场景的正射俯拍。分区按模型坐标绘制，比例尺为模型距离。',12,'#455b58')
txt(23,1241,'校界  © OpenStreetMap contributors，采用原项目东区范围   |   白线为制作分工边界，沿街建筑以完整单体交接。',12,'#455b58')
board.save(out/'东区开发分区图（项目模型俯视）.png',optimize=True)
print('zone percentages',np.round(np.bincount(ids.ravel())[1:]/(ids>0).sum()*100,1))
