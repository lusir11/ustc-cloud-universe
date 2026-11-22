"""East campus humanities wings A and C, in the project's east/south/up metre frame.

The athletics block doubles as B. Its link to A belongs to the assembly.
The two long frontages and the two different A–C links enclose an open court.
"""
from math import cos, pi, sin
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw


def garden_leaf_spray(seed=2044):
    """A small group of leafy shoots, shared by shrubs throughout the court."""
    rng = Random(seed)
    image = Image.new('RGBA',(256,256),(0,0,0,0))
    draw = ImageDraw.Draw(image)
    palette = ((73,100,56),(112,137,81),(122,142,69),(81,107,72),(142,149,91))
    for x1,y1 in ((38,98),(66,46),(99,23),(142,15),(191,37),(218,80),(242,119)):
        x0,y0 = 126+rng.randint(-25,25),248-rng.randint(0,17)
        x1 += rng.randint(-14,14)
        y1 += rng.randint(-9,22)
        bend = rng.uniform(-24,24)
        points=[]
        for k in range(13):
            t=k/12
            points.append((x0+(x1-x0)*t+bend*sin(t*pi),y0+(y1-y0)*t))
        draw.line(points,fill=(116,127,70,255),width=2)
        for k,(x,y) in enumerate(points[2:]):
            for side in (-1,1):
                length = rng.uniform(15,28)*(1-.037*k)
                tx,ty = x+side*length,y-rng.uniform(9,19)
                cx,cy=(x+tx)/2,(y+ty)/2
                w=rng.uniform(3.4,6.4)
                leaf = rng.choice(palette)
                draw.polygon([(x,y),(cx-side*w*.60,cy-w),(tx,ty),(cx+side*w*.60,cy+w)],fill=(*leaf,255))
                draw.line([(x,y),(cx,cy),(tx,ty)],fill=(*[min(255,c+16) for c in leaf],255),width=1)
    return image


def build(m):
    # Coordinates of the original shared OSM envelope, squared to the court.
    west, east = -337.9, -279.9
    an, ass = 541.30, 551.95
    cn, cs = 561.60, 567.04
    ac, cc = (an + ass) / 2, (cn + cs) / 2
    ah, ch = 15.82, 4.16
    box = m.box

    def block(name, mat, x, z, h, lx, lz, lh, solid=False):
        box('CB10_' + name, mat, (x, z, h), (lx, lz, lh))
        if solid:
            m.solid_box((x, z, h), (lx, lz, lh))

    def walkway(name, x0, x1, z0, z1, height=0.05):
        block(name, 'court_stone', (x0+x1)/2, (z0+z1)/2,
              height/2, x1-x0, z1-z0, height)
        m.solid_box(((x0+x1)/2,(z0+z1)/2,(height-.25)/2),(x1-x0,z1-z0,height+.25))

    m.material('court_stone', '#b5b6ad', roughness=0.93)
    m.material('humanities_sash', '#443d37', roughness=0.54, metallic=0.34)
    m.material('humanities_sill', '#b7aa91', roughness=0.83)
    m.material('humanities_spandrel', '#68625a', roughness=0.74)
    m.material('hall_glass', '#90aebc', roughness=0.18, metallic=0.19)
    glass = m.materials['hall_glass']
    glass['alphaMode'] = 'BLEND'
    glass['doubleSided'] = True
    glass['pbrMetallicRoughness']['baseColorFactor'][3] = .49
    m.material('humanities_green', '#729450', roughness=0.92)
    m.material('court_joints', '#a5a79f', roughness=0.98)
    m.material('court_soil', '#565145', roughness=0.95)
    m.material('shrub_shade', '#567049', roughness=0.92)
    m.material('shrub_tips', '#a2b96c', roughness=0.90)

    # A wall is assembled from masonry between the openings. Each window's glass
    # is recessed behind a lintel, lower panel, sill and a narrow metal frame.
    core_e = east - 5.0
    wall_len = core_e-west
    a_mid=(west+core_e)/2
    # Top-floor return behind the open east frame is set two bays back.
    # A continuous standard roof here used to fill the sky opening in side views.
    notch=core_e-2*wall_len/13
    edge=ass-5.71
    terrace_height=11.72
    def wing_mass(x0,x1,z0,z1,h,underside=0.0):
        dx=x1-x0; dz=z1-z0
        xx=(x0+x1)/2;zz=(z0+z1)/2
        mid=(h+underside)/2
        m.solid_box((xx,zz,mid),(dx,dz,h-underside))
        block('A_InnerShade','humanities_spandrel',xx,zz,mid,dx-.30,dz-.34,h-underside-.22)
        block('A_Cap','roof',xx,zz,h+.03,dx,dz,.19)
    wing_mass(west,notch,an,ass,ah)
    wing_mass(notch,core_e,edge,ass,ah)
    # At ground level the glazed oriel is a second mouth of the A/B passage.
    # The opening turns north under the east link and joins the bicycle lane.
    undercroft=4.17
    wing_mass(notch,core_e,an,edge,terrace_height,undercroft)
    block('A_PassageInnerReturn','brick',(notch+core_e)/2,edge+.04,undercroft/2,
          core_e-notch,.15,undercroft)
    block('A_PassageRearJamb','brick',notch+.04,(an+edge)/2,undercroft/2,
          .15,edge-an,undercroft)
    block('A_TerraceCheek','brick',(notch+core_e)/2,edge,(terrace_height+ah)/2,
          core_e-notch,.25,ah-terrace_height)
    block('A_TerraceBack','brick',notch,(an+edge)/2,(terrace_height+ah)/2,.25,edge-an,ah-terrace_height)
    # Inner bay recesses and physical lintel/sill edges give a real profile at
    # grazing angles. The A–B bridge meets the north wall over two of the bays.
    def facade_a(side, outward):
        z = an if outward < 0 else ass
        n = 13
        pitch=wall_len/n
        glw=2.28 if outward>0 else 1.56
        glz=z-outward*.19
        for floor in range(4):
            base = floor*3.90
            count=11 if floor in (0,3) and outward<0 else n
            run=count*pitch
            low, high = (0.27,3.10) if not floor else (0.92,3.20)
            for band,y0,y1 in [('Lower',base,base+low),('Upper',base+high,base+3.90)]:
                block('A_'+side+band,'brick',west+run/2,z,(y0+y1)/2,run,.31,y1-y0)
            for i in range(count+1):
                x=west+i*pitch;pw=pitch-glw
                if i==0:x+=pw/4;pw/=2
                if i==count:x-=pw/4;pw/=2
                block('A_'+side+'BrickPier','brick',x,z,base+(low+high)/2,pw,.31,high-low)
            for i in range(count):
                x=west+(i+.5)*pitch
                if outward<0 and floor in (1,2) and -296<x<-288:
                    continue
                frame=base+(low+high)/2
                block('A_'+side+'Sash','humanities_sash',x,glz,frame,glw,.12,high-low)
                panel=.43
                block('A_'+side+'Glass','glass',x,glz+outward*.078,frame+panel/2,
                      glw-.13,.035,high-low-panel-.12)
                block('A_'+side+'Apron','humanities_spandrel',x,glz+outward*.08,base+low+panel/2,glw-.13,.04,panel-.05)
                block('A_'+side+'Mullion','metal',x,glz+outward*.12,frame+.22,.052,.062,high-low-panel)
                block('A_'+side+'Vent','metal',x,glz+outward*.12,base+high-.52,glw-.1,.062,.048)
                block('A_'+side+'Lintel','humanities_sill',x,z+outward*.08,base+high+.12,glw+.13,.24,.24)
        block('A_'+side+'Parapet','brick',west+run/2,z,15.70,run,.34,.35)

    facade_a('South',1)
    facade_a('North',-1)
    # West gable with a cantilevered upper brick panel and black soffit.
    block('A_WestGable','brick',west,ac,ah/2,.34,ass-an,ah)
    for level in range(4):
        for dz in (-2.8,2.3):
            block('A_WestSash','humanities_sash',west-.18,ac+dz,1.9+3.9*level,.09,1.1,1.82)
            block('A_WestGlass','glass',west-.238,ac+dz,1.9+3.9*level,.04,.98,1.69)
            block('A_WestLintel','humanities_sill',west-.26,ac+dz,2.89+3.9*level,.24,1.36,.15)
    block('A_WestCantilever','brick',west-.28,an+1.52,10.20,.75,3.50,10.85)
    block('A_WestSoffit','dark',west-.28,an+1.52,4.72,.77,3.51,.18)
    # East end: the south half carries a perforated brick panel and a real crest.
    block('A_EastBacking','brick',core_e,(edge+ass)/2,ah/2,.22,ass-edge,ah)
    block('A_EastLowBacking','brick',core_e,(an+edge)/2,(terrace_height+undercroft)/2,
          .22,edge-an,terrace_height-undercroft)
    block('A_EastUpperFloor','concrete',(core_e+east)/2,ac,6.77,east-core_e,ass-an,.30)
    m.solid_box(((core_e+east)/2,ac,6.77),(east-core_e,ass-an,.30))
    block('A_EastCoping','roof',(core_e+east)/2,(edge+ass)/2,ah+.04,east-core_e,ass-edge,.17)
    # Reflected strip behind the silhouette, terminating below the overhead opening.
    bay_e=east-.82
    bay_y=(an+edge)/2
    block('A_OrielSoffit','humanities_spandrel',(notch+bay_e)/2,bay_y,4.28,
          bay_e-notch+.09,edge-an,.21,True)
    block('A_OrielSill','steel',bay_e+.02,bay_y,4.35,.15,edge-an,.21)
    for xx,zz,w,d in ((bay_e,bay_y,.12,edge-an-.28),((bay_e+core_e)/2,an+.14,bay_e-core_e,.12)):
        block('A_GlazedBay','glass',xx,zz,8.71,w,d,8.66)
    for i in range(5):
        zz=an+.14+i*(edge-an-.28)/4
        block('A_GlazedBayMullion','metal',bay_e+.07,zz,8.71,.09,.066,8.74)
    for h in (4.35,6.51,8.68,10.87,13.06):
        block('A_GlazedBayTransom','metal',bay_e+.07,bay_y,h,.10,edge-an-.18,.068)
    block('A_GlazedBayRoof','metal',(core_e+bay_e)/2,bay_y,13.09,bay_e-core_e,edge-an-.18,.16)
    m.solid_box(((core_e+bay_e)/2,bay_y,8.71),(bay_e-core_e,edge-an-.18,8.68))
    # The perforated panel stands proud of the wall. Its open cells reveal
    # a shaded masonry return, including from the low camera at the east gate.
    badge_z = ass - 3.38
    lattice_w, lattice_base, lattice_top = 4.30, 8.67, 14.85
    left, right = badge_z - lattice_w/2, badge_z + lattice_w/2
    for z0,z1,h0,h1 in ((edge,left,6.92,ah),(right,ass,6.92,ah),
                         (left,right,6.92,lattice_base),(left,right,lattice_top,ah)):
        block('A_CrestSurround','brick',east-.02,(z0+z1)/2,(h0+h1)/2,
              .32,z1-z0,h1-h0)
    m.solid_box((east-.02,(edge+ass)/2,(ah+6.92)/2),(.32,ass-edge,ah-6.92))
    # Continue the soffit/border over the rectangular opening beside the crest.
    block('A_CrownLintel','brick',east-.02,(an+edge)/2,ah-.44,.32,edge-an,.88)
    block('A_CrownReturn','brick',east-.02,an+.24,10.93,.32,.48,8.02)
    block('A_CrownSouthReturn','brick',(east+core_e)/2,ass-.13,11.32,east-core_e,.26,8.92)
    # Courses and headers form a running-bond grille with genuine openings.
    # Only two repeating header positions are needed across alternate courses.
    m.material('terracotta_screen','#a96449',.88)
    m.material('screen_recess','#352923',.97)
    block('A_LatticeRear','screen_recess',east-.34,badge_z,(lattice_base+lattice_top)/2,
          .08,lattice_w+.10,lattice_top-lattice_base+.12)
    for zz in (left,right):
        block('A_LatticeBorder','terracotta_screen',east+.145,zz,(lattice_base+lattice_top)/2,
              .16,.090,lattice_top-lattice_base+.10)
    for h in (lattice_base,lattice_top):
        block('A_LatticeBorder','terracotta_screen',east+.145,badge_z,h,.16,lattice_w,.093)
    rows, bays = 39, 20
    course = (lattice_top-lattice_base)/rows
    module = lattice_w/bays
    for j in range(rows):
        h = lattice_base + j*course
        block('A_LatticeCourse','terracotta_screen',east+.151,badge_z,h+.033,.125,lattice_w,.066)
        stagger = .5 if j%2 else 1
        headers = bays if j%2 else bays-1
        for k in range(headers):
            z = left + (k+stagger)*module
            block('A_LatticeHeader','terracotta_screen',east+.139,z,h+(course+.066)/2,
                  .101,.068,course-.066)
    seal=Path(__file__).with_name('humanities_seal.png')
    def rim(xx,r,ang):
        return (east+.155+xx,badge_z+r*cos(ang),12.04+r*sin(ang))
    for i in range(48):
        a,b = i*2*pi/48,(i+1)*2*pi/48
        m.face('steel',(rim(.069,1.255,a),rim(.069,1.255,b),rim(.130,1.255,b),rim(.130,1.255,a)))
        m.face('steel',(rim(.130,1.255,a),rim(.130,1.255,b),rim(.148,1.225,b),rim(.148,1.225,a)))
    m.image_sign('CB10_A_PhotoSeal',str(seal),(east+.304,badge_z,12.04),2.48,2.48,'east')
    m.sign('CB10_A_Name','人文楼',(east+.15,ass-.61,12.14),.65,2.39,'east')
    # A recessed stair at the east end, inside the colonnade. Its underside is solid.
    for i in range(12):
        y=(i+1)*.164
        block('A_ExteriorStair','stone',core_e+1.86,ass-.30-.31*i,y/2,3.06,.31,y,True)
    m.sign('CB10_A_Wing','A楼',(core_e-.89,ass+.177,3.24),.88,.42,'south')

    # C is the low brick museum/classroom wing along the opposite edge of the court.
    length=east-west
    mc=(east+west)/2
    block('C_Core','brick',mc,cc+0.12,ch/2,length,cs-cn-.24,ch,True)
    block('C_Coping','roof',mc,cc,ch+.03,length+.21,cs-cn+.18,.16)
    block('C_Socle','stone',mc,cn+.18,.18,length,.30,.32)
    pitch=length/13
    m.material('ivy_bronze','#78724c',roughness=.88)
    m.material('ivy_stem','#5e5541',roughness=.94)
    m.material('ramp_granite','#dedbd0',roughness=.85)
    m.image_for['ramp_granite']='cb10_aggregate'
    foliage = ('shrub_shade','humanities_green','ivy_bronze','shrub_tips')

    def ivy_trail(start_x,start_h,dx,dh,segments,seed):
        # Slender brown runners and individually folded ivy leaves catch light
        # at different angles on the lintel, jamb and brick face.
        previous = (start_x,cn-.241,start_h)
        for j in range(1,segments+1):
            t = j/segments
            xx = start_x+dx*t+(.11+.05*cos(seed))*sin(t*11+seed)*sin(t*pi)
            hh = start_h+dh*t+(.075+.045*sin(seed))*cos(t*8+seed)*sin(t*pi)
            yy = cn-.25-.034*(1+cos(t*9+seed))
            point = (xx,yy,hh)
            m.quad('C_IvyStem','ivy_stem',(
                previous,point,(xx+.011,yy,hh+.010),
                (previous[0]+.011,previous[1],previous[2]+.010)))
            for side in (-1,1):
                scale = .034+.020*(1+sin(seed*2.17+j*1.33+side))
                cx = xx+side*scale*.64
                cy = yy-.018
                cz = hh+scale*.23*cos(j*2.29)
                tip = (cx+side*scale*.79,cy-scale*.34,cz-scale)
                mid = (cx,cy-.029,cz)
                outline = [(cx-side*scale*.55,cy,cz+scale*.73),
                           (cx+side*scale*.29,cy,cz+scale*.87),
                           (cx+side*scale*.90,cy,cz+scale*.32),
                           tip,(cx-side*scale*.74,cy,cz-scale*.09)]
                mat = foliage[(seed+j+(side==1))%len(foliage)]
                # Consistently face north, including mirrored leaves.
                if side==1:
                    outline.reverse()
                for k,corner in enumerate(outline):
                    m.face(mat,(mid,corner,outline[(k+1)%len(outline)]))
            previous = point

    for i in range(13):
        x=east-(i+.5)*pitch
        if i==9:
            # A blind masonry bay shares the museum's broad stone landing.
            block('C_MuseumBrickPanel','brick',x,cn+.05,1.84,2.65,.31,3.30)
        elif i in (1,4,8):
            room={1:'C101',4:'C102',8:'钱邻照科学史博物馆'}[i]
            block('C_DoorFrame','humanities_sash',x,cn-.04,1.77,2.70,.15,2.96)
            block('C_DoorFanlight','glass',x,cn-.132,2.88,2.54,.042,.53)
            block('C_DoorTransom','metal',x,cn-.162,2.55,2.65,.064,.11)
            if i==8:
                for offset in (-.61,.61):
                    block('C_MuseumDoorGlass','glass_dark',x+offset,cn-.139,1.44,1.10,.049,2.06)
                    block('C_DoorHandle','steel',x+offset*.25,cn-.205,1.40,.036,.092,.45)
                plate_x=x+1.65
            else:
                # Facing C from the courtyard, the display window is left
                # of the solid classroom door. Its pull sits near the jamb.
                block('C_DoorPane','glass_dark',x+.55,cn-.137,1.60,1.30,.053,1.77)
                block('C_ClassroomDoor','humanities_spandrel',x-.74,cn-.14,1.42,1.03,.055,2.13)
                block('C_DoorHandle','steel',x-.38,cn-.208,1.40,.033,.091,.29)
                plate_x=x-1.63
            plate_w=.83 if i==8 else .54
            block('C_NamePlate','blue',plate_x,cn-.17,2.67,plate_w,.04,.20)
            m.sign('CB10_C_Room',room,(plate_x,cn-.195,2.67),plate_w-.05,.13,'north')
        else:
            block('C_CourtFrame','humanities_sash',x,cn+.025,1.79,2.71,.16,2.92)
            block('C_CourtGlass','glass_dark',x,cn-.071,1.96,2.53,.05,2.45)
            block('C_LowerPanel','humanities_spandrel',x,cn-.11,.68,2.52,.075,.72)
            for off in (-.44,.48):
                block('C_NarrowMullion','metal',x+off,cn-.12,1.79,.06,.08,2.91)
            block('C_Transom','metal',x,cn-.12,2.75,2.68,.09,.062)
        block('C_PaleLintel','humanities_sill',x,cn-.14,3.36,2.91,.30,.20)
        block('C_BrickPilaster','brick',x-pitch*.41,cn+.045,1.89,.36,.41,3.68)
        if i in (0,1,3,4,7,8):
            rng=Random(192+i)
            runner_start=x-1.65+rng.uniform(-.48,.42)
            runner_len=rng.uniform(2.37,3.72)
            ivy_trail(runner_start,3.85,runner_len,-.17,39,i)
            for j,offset in enumerate((-1.54,-1.37,-.96,-.41,.15,.73,1.27,1.51)):
                drop=rng.uniform(.69,2.24) if abs(offset)>1.1 else rng.uniform(.09,.60)
                if abs(offset)<1 and rng.random()<.50:
                    continue
                ivy_trail(x+offset+rng.uniform(-.15,.15),3.77,rng.uniform(-.45,.45),-drop,4+int(drop*9),i*7+j)
            # At C101 and C102 the runners spread across masonry piers and up
            # onto the parapet, well beyond the outline of the window frame.
            if i in (1,4,7):
                for j in range(8):
                    sx=x-1.38+rng.uniform(-.36,.12)
                    h=rng.uniform(2.96,3.69)
                    ivy_trail(sx,h,rng.uniform(-1.52,-.36),rng.uniform(-.48,.29),16,i*19+j)
                ivy_trail(runner_start+.40,3.81,-.87,.24,17,61+i)
    # The museum landing spans its doors and the blind bay immediately west.
    for i in (1,4,8):
        x=east-(i+.5)*pitch
        if i==1:
            # C101 has a short two-piece ramp, sloping up from the courtyard.
            for lane in (-.68,.68):
                xx=x+lane
                for k in range(5):
                    ht=.052+.044*k
                    block('C_RampBase','stone',xx,cn-1.24+k*.236,ht/2,1.35,.236,ht,True)
                m.quad('C_RampFinish','ramp_granite',((xx-.665,cn-1.358,.061),
                       (xx+.665,cn-1.358,.061),(xx+.665,cn-.178,.281),(xx-.665,cn-.178,.281)))
            # A narrow recessed joint lets the two pale slabs read separately.
            m.quad('C_RampJoint','humanities_spandrel',((x-.017,cn-1.358,.057),
                   (x+.017,cn-1.358,.057),(x+.017,cn-.178,.277),(x-.017,cn-.178,.277)))
        else:
            width = pitch*1.88 if i==8 else 2.75
            x -= pitch*.50 if i==8 else 0
            for j in range(3):
                ht=(j+1)*.115
                block('C_EntranceTreads','stone',x,cn-.19-(2.5-j)*.38,ht/2,width,.38,ht,True)
                block('C_TreadNosing','humanities_sill',x,cn-.19-(3-j)*.38,ht-.016,
                      width+.022,.063,.041)
    m.sign('CB10_C_Wing','C楼',(east-2.13,cn-.21,3.75),.84,.37,'north')

    # A/C courtyard: one transparent connector at the far end and a distinct
    # open street portal at the east. The sightline from the east stays clear.
    gx=west+11.1
    span=cn-ass
    gz=(cn+ass)/2
    glazing_height=8.08
    depth = 4.17
    block('AC_GlazedLinkRoof','metal',gx,gz,glazing_height,depth+.25,span+.24,.22,True)
    block('AC_LinkSecondSlab','humanities_spandrel',gx,gz,3.39,depth,span,.25,True)
    walkway('AC_LinkFloor',gx-depth/2,gx+depth/2,ass+.14,cn-.12)
    # A paved rear approach remains visible through the paired glass entrances.
    walkway('AC_RearCourt',west-1.1,gx-depth/2,ass+.15,cn-.13)
    m.material('hall_floor','#acaaa2',roughness=.48)
    block('AC_HallTerrazzo','hall_floor',gx,gz,.057,depth-.08,span-.35,.013)
    block('AC_HallCeiling','concrete',gx,gz,3.235,depth-.12,span-.31,.074)
    m.material('hall_lighting','#fff7dc',roughness=.46)
    m.materials['hall_lighting']['emissiveFactor']=[.84,.76,.53]
    for xx in (gx-1.42,gx+1.42):
        block('AC_HallLightChannel','metal',xx,gz,3.182,.15,span-1.88,.045)
        block('AC_HallDiffuser','hall_lighting',xx,gz,3.151,.084,span-2.08,.025)
    for j in range(5):
        xx=west-1.1+j*2
        block('AC_RearPavingJoint','court_joints',xx,gz,.052,.026,span-.31,.004)
    # Brick at the C-wing end continues above its one-storey roof.
    cheek = 1.50
    z0, z1 = ass+.11, cn-cheek
    centre = (z0+z1)/2
    block('AC_LinkBrickCheek','brick',gx,cn-cheek/2,glazing_height/2,
          depth,cheek,glazing_height,True)
    door_half = 1.22
    for side in (-1,1):
        xx = gx+side*depth/2
        front = xx+side*.14
        block('AC_LinkUpperGlass','hall_glass',xx,centre,5.77,.042,z1-z0,4.37)
        m.solid_box((xx,centre,5.77),(.09,z1-z0,4.37))
        for j in range(7):
            z = z0+(z1-z0)*j/6
            block('AC_LinkMullion','metal',xx+side*.048,z,5.75,.12,.069,4.49)
        block('AC_LinkRail','metal',xx+side*.05,centre,5.77,.12,z1-z0,.064)
        block('AC_LinkFascia','metal',front,centre,3.46,.34,z1-z0+.1,.29)
        # Two partly open leaves preserve a clear route through the lobby.
        for direction in (-1,1):
            jamb = centre+direction*door_half
            outer = z0 if direction==-1 else z1
            mid, width = (jamb+outer)/2, abs(outer-jamb)
            block('AC_LinkLowerGlass','hall_glass',xx,mid,1.71,.042,width,3.27)
            m.solid_box((xx,mid,1.71),(.09,width,3.27))
            for zz in (jamb,outer,mid):
                block('AC_LinkDoorJamb','metal',front,zz,1.72,.11,.068,3.27)
            far = (xx-side*.92,jamb-direction*.60)
            mid_x, mid_z = (xx+far[0])/2,(jamb+far[1])/2
            angle = direction*side*.578
            for h,thick,mat in ((1.32,2.23,'hall_glass'),(.18,.12,'metal'),(2.46,.10,'metal')):
                box('CB10_AC_LinkDoorGlass',mat,(mid_x,mid_z,h),(1.10,.055,thick),angle)
            block('AC_LinkDoorStile','metal',far[0],far[1],1.32,.068,.068,2.39)
            m.solid_box((mid_x,mid_z,1.29),(1.10,.08,2.45),angle)
        block('AC_LinkDoorHead','metal',front,centre,2.54,.12,2*door_half,.09)
        block('AC_LinkLights','hall_glass',xx,centre,2.92,.042,2*door_half,.66)
        block('AC_LinkLowerRail','metal',xx+side*.05,centre,2.54,.11,z1-z0,.056)
    m.sign('CB10_AC_LobbyCaptionShadow','人 文 楼',(gx+depth/2+.125,centre-.036,3.94),
           2.92,.64,'east',color='#353c40')
    m.sign('CB10_AC_LobbyCaption','人 文 楼',(gx+depth/2+.15,centre,3.98),
           2.92,.64,'east',color='#f5f3e7')
    m.materials['sign_人 文 楼_f5f3e7']['emissiveFactor'] = [.29,.28,.25]
    block('AC_HallSignBase','red',gx+2.31,cn-2.00,.21,.31,1.89,.31)
    m.sign('CB10_AC_Threshold','USTC  新人文',(gx+2.48,cn-2.00,.50),
           1.96,.30,'east',color='#eeeeea')
    walkway('Court_Pavers',gx+2.15,east+1.85,ass+.16,cn-.18)
    # The paving and planted islands follow the walk past C101/C102. Keep the
    # entrances, full width of the museum steps and the middle path unobstructed.
    paving_start=gx+2.15
    for j in range(1,int((east+1.85-paving_start)/1.22)+1):
        xx=paving_start+j*1.22
        block('Court_PaverJoint','court_joints',xx,gz,.052,.018,span-.39,.003)
    for j in range(1,int((span-.35)/.74)+1):
        zz=ass+.16+j*.74
        block('Court_PaverJoint','court_joints',(paving_start+east+1.85)/2,zz,.053,
              east+1.85-paving_start,.017,.003)

    for mat,tint,seed in (('garden_shoot','#f8f2e3',2044),
                          ('garden_underleaf','#cad0a9',2049)):
        m.textures[mat] = garden_leaf_spray(seed)
        m.material(mat,tint,.88)
        m.materials[mat].update(alphaMode='MASK',alphaCutoff=.33,doubleSided=True)
        m.image_for[mat]=mat

    def leaf_spray(x,z,h,width,height,angle,lean,mat):
        dx,dz = .5*width*cos(angle),.5*width*sin(angle)
        ox,oz = lean*sin(angle),-lean*cos(angle)
        m.face(mat,((x-dx,z-dz,h),(x+dx,z+dz,h),
                    (x+dx+ox,z+dz+oz,h+height),(x-dx+ox,z-dz+oz,h+height)),
               ((0,1),(1,1),(1,0),(0,0)))

    def planting(name,x,z,rx,rz,seed):
        # Rectangular borders leave clear breaks at each threshold. Narrow
        # shoots overlap at their roots and remain individually readable above.
        d=min(.24,rx*.45,rz*.45)
        outline=[(x-rx+d,z-rz),(x+rx-d,z-rz),(x+rx,z-rz+d),(x+rx,z+rz-d),
                 (x+rx-d,z+rz),(x-rx+d,z+rz),(x-rx,z+rz-d),(x-rx,z-rz+d)]
        m.prism(name+'_kerb','humanities_sill',outline,.055,.141)
        m.prism(name+'_soil','court_soil',[(x+(xx-x)*(1-.06/rx),z+(zz-z)*(1-.06/rz))
                                           for xx,zz in outline],.140,.151)
        if name in ('CourtBorder','RearTreeBed'):
            # These beds receive the reference-modelled plants in Blender and Godot.
            return
        rng=Random(1513+seed)
        long_x=rx>=rz
        length,breadth=(rx,rz) if long_x else (rz,rx)
        groups=max(2,round(length*3.6))
        phase=rng.uniform(0,2*pi)
        for j in range(groups):
            envelope=.68+.32*cos(phase+j*.72)
            for row in (-1,0,1):
                if row and envelope<.52 and rng.random()<.75:
                    continue
                longitudinal=(j+.5+rng.uniform(-.19,.19))*2*length/groups-length
                cross=breadth*(.61*row+rng.uniform(-.12,.12))
                xx=x+(longitudinal if long_x else cross)
                zz=z+(cross if long_x else longitudinal)
                if name=='GatePlanting' and (xx-(east-.11))**2+(zz-548.28)**2 < .48**2:
                    continue
                height=rng.uniform(.40,.75)*envelope*(1.09 if row==0 else .86)
                start=rng.uniform(0,2*pi)
                for k in range(3):
                    angle=start+k*2*pi/3
                    mat='garden_underleaf' if k==0 else 'garden_shoot'
                    leaf_spray(xx,zz,.15,rng.uniform(.57,1.03)*(.62+envelope*.52),height*rng.uniform(.85,1.12),
                               angle,rng.uniform(.12,.39),mat)
                # Long fine blades and lighter tips along the flower-bed edge.
                if row!=0:
                    for k in range(8):
                        a=start+k*2.399
                        dx,dz=cos(a),sin(a)
                        w=rng.uniform(.014,.035)
                        lean=rng.uniform(.13,.24)
                        tip=(xx+lean*dx,zz+lean*dz,.32+rng.uniform(.07,.28))
                        m.face('shrub_tips',((xx-w*dz,zz+w*dx,.15),(xx+w*dz,zz-w*dx,.15),tip))

    # C101 (x=-286.6), C102 (-300.0) and the museum's long landing
    # (-324.3 to -315.8) each have a full-width paved approach.
    beds = ((-284.82,-279.50,560.52,.84),(-298.25,-288.42,560.37,.98),
            (-307.73,-301.82,560.49,.89),(-315.43,-308.41,560.45,.93),
            (-324.48,-317.26,553.01,.80),(-316.20,-308.31,552.94,.73),
            (-307.05,-300.51,553.02,.83),(-299.17,-290.63,553.06,.88),
            (-289.50,-287.02,552.94,.77),(-284.09,-280.02,553.04,.84))
    def specimen(kind,x,z,base,scale,yaw):
        m.planting.append({"kind":kind,"position":[round(x,4),base,round(z,4)],
                           "scale":round(scale,4),"rotation_y":round(yaw,6)})
        # The gate stays walkable between pots. Only hard pots and trunks
        # get obstacles; the leaves overhanging each flower bed remain soft.
        trunk={'ornamental':(.074,1.1),'background_tree':(.17,2.4),'entrance_pot':(.166,.34)}
        if kind in trunk:
            radius,height=trunk[kind]
            m.solid([(x+scale*radius*cos(i*pi/6),z+scale*radius*sin(i*pi/6))
                     for i in range(12)],base,base+height*scale)

    for j,(x0,x1,zz,rz) in enumerate(beds):
        planting('CourtBorder',(x0+x1)/2,zz,(x1-x0)/2,rz,j)
        rng=Random(8307+j)
        count=max(1,round((x1-x0)/2.03))
        spacing=(x1-x0)/count
        for i in range(count):
            specimen('courtyard_shrub', x0+spacing*(i+.5)+rng.uniform(-.09,.09),
                     zz+(.14 if zz<555 else 0)+rng.uniform(-.075,.075), .151, rng.uniform(.76,1.02),
                     rng.uniform(-pi,pi))

    # Garden canopy at the rear approach, offset from the central glass doors.
    planting('RearTreeBed',-337.28,557.94,1.4,.87,49)
    specimen('background_tree',-337.28,557.94,.151,1.34,.1584)

    def shrub(x,z,height,radius,seed):
        rng=Random(seed)
        for i in range(6):
            a=seed+i*2.399
            dx=radius*cos(a); dz=radius*.70*sin(a)
            fork=(x+dx*.22,z+dz*.22,.36*height)
            m.beam('CB10_ShrubStem','ivy_stem',(x+.05*cos(i),z+.045*sin(i),.17),
                   fork,.039+.008*(i%3))
            for j in range(4):
                twig=a+(j-1.5)*.55
                fraction=rng.uniform(.40,.83)
                end=(fork[0]+fraction*radius*cos(twig),fork[1]+fraction*radius*sin(twig),
                     height*rng.uniform(.50,.81))
                m.beam('CB10_ShrubBranch','ivy_stem',fork,end,.023)
                for k in range(3):
                    leaf_spray(*end,radius*rng.uniform(.63,1.02),height*rng.uniform(.25,.40),
                               twig+k*1.08,radius*rng.uniform(.15,.39),
                               'garden_shoot' if (i+k)%3 else 'garden_underleaf')

    shrub(gx+3.35,ass+1.02,2.80,1.16,11)
    shrub(gx+2.63,cn-.98,1.45,.74,18)
    # The ornamental tree takes the indicated place between two right-hand piers.
    specimen('ornamental',east-.12,548.28,.151,1.0,.92)
    shrub(east-.37,cn+1.61,2.10,.90,12)
    # C and the research institute plaque are at the south edge of the entrance.
    px = east+1.12
    north, south = ass+1.87, cn-.47
    # Matched pots flank the opening, forward of the signs and off the through route.
    for zz,yaw in ((north+.96,.35),(south-.96,-.57)):
        specimen('entrance_pot',px+.64,zz,.05,1.12,yaw)
    gate_pitch = 1.23
    for anchor,direction,count,label in (
        (south,1,2,'科技人文高等研究院'),
        (north,-1,5,'人文与社会科学学院')
    ):
        for i in range(count+1):
            zz = anchor+direction*gate_pitch*i
            block('GatePier','brick',px,zz,1.91,.76,.76,3.82,True)
            block('GateCap','metal',px,zz,3.86,.84,.84,.092)
            if i in (count, 0 if direction==1 else 1):
                block('GateUpperPost','ivory',px,zz,4.87,.50,.49,1.96)
            if i==0:
                block('GatePlaque','white',px+.398,zz,2.04,.064,.61,3.23)
                m.sign('CB10_Plaque',label,(px+.437,zz,1.79),.41,2.39,'east',color='#242725')
                for offset,small_text in ((-.10,'中国科学'),(.10,'技术大学')):
                    m.sign('CB10_PlaqueHeader',small_text,(px+.437,zz+offset,3.27),
                           .10,.45,'east',color='#242725')
        planting('GatePlanting',px-.85,anchor+direction*gate_pitch*count/2,
                 .52,max(.7,gate_pitch*count*.46),count+5)
        # Each street-side bed starts beyond its nameboard, in front of the
        # unmarked shafts. The signed piers and their whole opening stay clear.
        planting('GateStreetBorder',px+.69,anchor+direction*gate_pitch*(count+1)/2,
                 .43,gate_pitch*(count-.45)/2,34+count)
    zmin, zmax = north-5*gate_pitch-.42,south+2*gate_pitch+.42
    for xx in (px+.39,px-2.80):
        block('GateFascia','concrete',xx,(zmin+zmax)/2,5.91,.36,zmax-zmin,.44,True)
        block('GateCoping','steel',xx,(zmin+zmax)/2,6.15,.39,zmax-zmin+.04,.06)
    for i in range(11):
        z = north+(south-north)*i/10
        block('GatePergolaRib','concrete',px-1.21,z,5.85,3.20,.23,.28)
    for z0,z1 in ((zmin,north),(south,zmax)):
        block('GateEaveDeck','concrete',px-1.18,(z0+z1)/2,5.79,3.14,z1-z0,.18,True)
