"""CB05 / Humanities B. Coordinates are east, south, up, in campus metres."""

import math


class Elevation:
    """A straight facade, measured along the wall and outward from its face."""

    def __init__(self, mesh, name, side, plane):
        self.mesh, self.name, self.side, self.plane = mesh, name, side, plane

    def point(self, u, d, h):
        if self.side == "east":
            return self.plane + d, u, h
        if self.side == "west":
            return self.plane - d, u, h
        if self.side == "north":
            return u, self.plane - d, h
        return u, self.plane + d, h

    def rect(self, name, mat, start, end, inside, outside, low, high):
        if end <= start or high <= low:
            return
        size = (outside-inside, end-start, high-low)
        if self.side in ("north", "south"):
            size = (size[1], size[0], size[2])
        self.mesh.box(self.name+"_"+name, mat,
                      self.point((start+end)/2, (inside+outside)/2, (low+high)/2), size)

    def band(self, start, end, low, high, openings):
        last = start
        for left, right in sorted(openings):
            self.rect("brick_pier","brick",last,left,-.37,0,low,high)
            last = right
        self.rect("brick_pier","brick",last,end,-.37,0,low,high)

    def window(self, u, w, low, high, blind=False):
        l, r = u-w/2, u+w/2
        self.rect("recess", "metal",l,r,-.34,-.29,low,high)
        self.rect("blue_glass","office_glass",l+.07,r-.07,-.28,-.23,low+.12,high-.14)
        self.rect("pale_lintel","ivory",l-.03,r+.03,-.13,.055,high-.17,high)
        self.rect("slender_sill","metal",l-.035,r+.035,-.27,.025,low,low+.085)
        self.rect("aluminium_mullion","metal",u-.023,u+.023,-.23,-.19,low+.11,high-.16)
        self.rect("upper_light","metal",l+.045,r-.045,-.23,-.19,high-.72,high-.674)
        if low < 1:
            self.rect("blind_spandrel","smoke_spandrel",l+.045,r-.045,-.215,-.17,low+.08,low+.57)
        if blind:
            top=high-.21
            self.rect("roller_blind","slate_blind",l+.08,r-.08,-.215,-.18,top-.60,top)
            for i in range(7):
                y=top-.07-i*.075
                self.rect("roller_slat","steel",l+.08,r-.08,-.175,-.154,y-.012,y)

    def facade(self, left, right, top, centers, door=None):
        rows=[(.42,3.95),(5.10,7.62),(8.53,11.02),(11.94,14.28)]
        last=0
        for idx,(low,high) in enumerate(rows):
            if high > top-.12:
                continue
            holes=[(u-w/2,u+w/2) for u,w in centers if idx or
                   door is None or u+w/2<=door[0] or u-w/2>=door[1]]
            if idx==0 and door:
                holes.append(door)
            self.band(left,right,last,low,[door] if idx==0 and door else [])
            self.band(left,right,low,high,holes)
            for j,(l,r) in enumerate(holes):
                if idx or not door or (l,r)!=door:
                    self.window((l+r)/2,r-l,low,high,blind=(idx==0 and j%3==0))
            last=high
        self.band(left,right,last,top,[])
        self.rect("coping","roof",left,right,-.31,.04,top,top+.10)


def curved_end(m):
    # The nose projects north of the east bar. Construct the glazing and masonry
    # around the semicircle, so views along the drive see the curved silhouette.
    cx, cz, radius, top = -291.85,502.00,4.50,15.03
    segments=24
    def point(i,r):
        a=math.pi+math.pi*i/segments
        return cx+r*math.cos(a),cz+r*math.sin(a)
    def arc_band(name,mat,r_inner,r_outer,h0,h1,i0=0,i1=segments):
        outline=[point(i,r_outer) for i in range(i0,i1+1)]
        outline.extend(point(i,r_inner) for i in range(i1,i0-1,-1))
        m.prism(name,mat,outline,h0,h1)
    footprint=[point(i,radius) for i in range(segments+1)]
    m.solid(footprint,0,top)
    m.prism("round_backing","brick",[point(i,radius-.32) for i in range(segments+1)],0,top)
    arc_band("granite_toe","stone",radius-.28,radius+.14,0,.28)
    arc_band("dark_skirt","smoke_spandrel",radius-.18,radius+.10,.28,1.03)
    arc_band("curved_glass","office_glass",radius-.19,radius,1.03,4.02)
    arc_band("transom","metal",radius-.06,radius+.04,3.20,3.26)
    for i in range(0,segments+1,2):
        x,z=point(i,radius+.012)
        m.box("curved_mullion","metal",(x,z,2.53),(.063,.063,3.02))
    for low,high,mat in [(4.02,4.15,"steel"),(4.15,4.52,"ivory"),(4.52,4.56,"metal"),
                         (4.56,4.75,"ivory"),(4.75,5.15,"brick"),(7.62,8.55,"brick"),
                         (11.02,11.95,"brick"),(14.28,top,"brick")]:
        arc_band("radial_course",mat,radius-.33,radius+(.11 if high<=4.75 else 0),low,high)
    for low,high in [(5.15,7.62),(8.55,11.02),(11.95,14.28)]:
        for i in range(0,segments,4):
            arc_band("radial_pier","brick",radius-.33,radius,low,high,i,i+2)
            arc_band("radial_frame","metal",radius-.31,radius-.15,low,high,i+2,i+4)
            arc_band("radial_window","office_glass",radius-.155,radius-.13,low+.09,high-.15,i+2,i+4)
            arc_band("radial_lintel","ivory",radius-.20,radius+.025,high-.14,high,i+2,i+4)
            arc_band("radial_transom","metal",radius-.13,radius-.09,high-.64,high-.59,i+2,i+4)
    m.prism("radial_roof","roof",footprint,top,top+.13)


def entrance(m,e):
    l,r=508.0,515.4
    # The real glazed entrance is recessed under a deep stone-edged canopy.
    e.rect("vestibule_back","ivory",l,r,-2.68,-2.54,.30,4.0)
    e.rect("vestibule_floor","tile",l,r,-2.58,-.15,.27,.34)
    e.rect("vestibule_ceiling","ivory",l,r,-2.58,-.15,3.89,4.04)
    for edge in (l,r):
        e.rect("vestibule_jamb","ivory",edge-.10,edge+.10,-2.66,-.25,.32,3.93)
    e.rect("inner_door","metal",l+1.1,l+2.15,-2.52,-2.45,.32,2.57)
    for u in [l+1.45,l+3.7,r-1.35]:
        ring=[e.point(u+.46*math.cos(math.tau*j/16),-1.32+.46*math.sin(math.tau*j/16),3.49)
              for j in range(16)]
        for p,q in zip(ring,ring[1:]+ring[:1]):
            m.beam("ring_luminaire","white",p,q,.047,.057)
    e.rect("glazed_entry","door_glass",l+.06,r-.06,-.25,-.18,.36,3.94)
    for u in (l,l+1.49,l+2.93,l+4.42,l+5.90,r):
        e.rect("door_stile","metal",u-.034,u+.034,-.22,-.12,.35,3.97)
    for y in (.37,2.68,3.86):
        e.rect("door_transom","metal",l,r,-.19,-.105,y,y+.065)
    e.rect("blue_safety_band","blue",l+.06,r-.06,-.145,-.125,1.55,1.62)
    for u in (511.53,511.84):
        e.rect("door_pull","steel",u-.028,u+.028,-.13,.05,1.08,1.83)
    e.rect("upper_fascia","stone",503.75,524.15,-.08,1.74,4.42,4.67)
    e.rect("canopy_shadow_gap","metal",503.75,524.15,-.07,1.68,4.35,4.42)
    e.rect("canopy_soffit","concrete",503.75,524.15,-.07,1.67,4.25,4.35)
    for u in [505.8,509.0,512.2,515.4,518.6,521.8]:
        e.rect("downlight","white",u-.09,u+.09,.97,1.15,4.22,4.25)
    # Ramp beside the three street steps, parallel rails as in southeast photo.
    m.box("entry_landing","stone",(-286.60,511.70,.17),(1.57,8.05,.34))
    m.solid_box((-286.60,511.70,.17),(1.57,8.05,.34))
    for i in range(3):
        outer=-285.81+(3-i)*.35
        m.box("entry_step","concrete",((outer-285.86)/2,511.32,.056*(i+1)),
              (outer+285.86,7.30,.112*(i+1)))
        m.solid_box(((outer-285.86)/2,511.32,.056*(i+1)),(outer+285.86,7.30,.112*(i+1)))
        m.box("step_nosing","ivory",(outer-.018,511.32,.112*(i+1)-.014),(.050,7.31,.031))
    for x in [-287.15,-285.83]:
        for h in [.52,.91]:
            m.beam("access_rail","metal",(x,515.70,h+.34),(x,522,h+.025),.045,.045)
        for i in range(6):
            z=515.70+1.26*i; floor=.34-.063*i
            m.box("rail_post","metal",(x,z,floor+.455),(.04,.04,.91))
    for x in [-287.19,-285.77]:
        # Ramp side and top; front edge is flush to the sidewalk.
        m.quad("ramp_side","stone",[(x,515.60,0),(x,515.60,.34),(x,522.16,.025),(x,522.16,0)])
    m.quad("ramp_walk","concrete",[(-287.19,515.6,.34),(-285.77,515.6,.34),(-285.77,522.16,.025),(-287.19,522.16,.025)])
    for i in range(12):
        height=.34-.315*(i+.5)/12
        m.solid_box((-286.48,515.60+6.56*(i+.5)/12,height/2),(1.42,6.56/12,height))
    e.rect("gym_plaque_back","stone",515.45,515.97,.013,.055,1.82,2.26)
    m.sign("gym_plaque","乒乓球馆",e.point(515.71,.061,2.04),.47,.15,"east")
    e.rect("access_notice","blue",515.50,515.92,.014,.054,1.16,1.71)


def build(m):
    m.material("office_glass","#4e6a77",roughness=.24,metallic=.30)
    m.material("door_glass","#66848a",roughness=.19,metallic=.27)
    m.materials["door_glass"]["alphaMode"]="BLEND"
    m.materials["door_glass"]["pbrMetallicRoughness"]["baseColorFactor"][3]=.34
    m.material("smoke_spandrel","#38434a",roughness=.48,metallic=.18)
    m.material("slate_blind","#737775",roughness=.58,metallic=.15)
    # Rectilinear parts meet flush; the surrounding facade shells carry
    # the actual deep reveals and reveal shadows.
    def core(name,x0,x1,z0,z1,top):
        underside=4.0 if name=="east_spine" else 0.0
        m.box(name+"_core","brick",((x0+x1)/2,(z0+z1)/2,(top+underside)/2),
              (x1-x0-.70,z1-z0-.70,top-underside))
        if underside:
            m.box(name+"_vestibule_backing","brick",((x0+x1-3.)/2,(z0+z1)/2,2.),
                  (x1-x0-3.70,z1-z0-.70,4.))
        m.box(name+"_roof","roof",((x0+x1)/2,(z0+z1)/2,top-.02),
              (x1-x0,z1-z0,.14))
        m.solid_box(((x0+x1)/2,(z0+z1)/2,top/2),(x1-x0,z1-z0,top))
    core("east_spine",-296.35,-287.35,502.,529.77,15.03)
    core("hall",-321.58,-296.31,512.12,529.67,14.80)
    core("west_bay",-324.52,-321.55,514.60,529.63,15.20)
    core("northwest_stair",-321.56,-315.70,506.56,512.14,15.72)
    curved_end(m)
    east=Elevation(m,"B_east","east",-287.35)
    east.facade(502,529.77,15.03,
                [(503.63,1.72),(506.74,1.78),(509.98,1.80),(513.19,1.80),
                 (516.91,1.76),(520.15,1.80),(523.44,1.78),(526.84,1.78)],(508.,515.4))
    entrance(m,east)
    west=Elevation(m,"B_west","west",-324.52)
    west.facade(514.6,529.63,15.20,[(516.61,1.90),(520.14,1.94),(523.78,1.94),(527.37,1.91)])
    # Short returns shade the west projection seen from the parked-car drive.
    for plane,side in [(514.60,"north"),(529.63,"south")]:
        wall=Elevation(m,"B_west_return",side,plane)
        wall.band(-324.52,-321.52,0,15.20,[])
    south=Elevation(m,"B_south","south",529.68)
    south.facade(-321.57,-296.32,14.80,[(x,1.64) for x in [-319.18,-315.4,-311.68,-307.9,-304.1,-300.42]])
    south.band(-296.36,-287.35,0,15.03,[])  # A/B bridge lands on this face
    north=Elevation(m,"B_north","north",512.12)
    north.facade(-315.70,-296.33,14.8,[(x,1.32) for x in [-313.8,-310.25,-306.55,-302.86,-299.1]])
    # Secondary low vestibule and isolated stair tower behind the rounded nose.
    lx,rx,z0,z1=-315.72,-299.5,508.8,512.22
    core("north_vestibule",lx,rx,z0,z1,5.05)
    n=Elevation(m,"B_service","north",z0)
    n.band(lx,rx,0,5.05,[(-311.08,-308.70)])
    n.rect("service_door","smoke_spandrel",-311.08,-308.70,-.25,-.16,.30,3.15)
    m.material("powder_coat","#59696e",roughness=.7)
    n.rect("door_leaf","powder_coat",-310.99,-308.79,-.14,-.09,.30,2.58)
    n.rect("door_meeting_stile","metal",-309.923,-309.902,-.09,-.073,.30,2.58)
    n.rect("door_head","ivory",-311.12,-308.67,-.12,.05,3.14,3.32)
    n.rect("door_canopy","metal",-311.48,-308.32,.0,.79,3.56,3.73)
    n.rect("door_handle","steel",-309.1,-309.04,-.08,.02,1.06,1.45)
    for i in range(3):
        n.rect("service_step","concrete",-311.28,-308.50,0,(3-i)*.32,0,.10*(i+1))
        m.solid_box((-309.89,z0-(3-i)*.16,.05*(i+1)),(2.78,(3-i)*.32,.10*(i+1)))
    for x in (-311.3,-308.48):
        for away,floor in ((.88,.1),(.12,.3)):
            m.box("newel","steel",(x,z0-away,floor+.43),(.036,.036,.86))
        m.beam("service_handrail","steel",(x,z0-.88,.96),(x,z0-.12,1.16),.045)
    for x in (rx,lx):
        face=Elevation(m,"B_vestibule_end","east" if x==rx else "west",x)
        face.band(z0,z1,0,5.05,[])
    stair=Elevation(m,"B_stair","north",506.56)
    stair.facade(-321.56,-315.70,15.72,[(-317.26,1.12)])
    side=Elevation(m,"B_stair_west","west",-321.56)
    side.facade(506.56,514.64,15.72,[(510.66,1.39),(513.08,1.24)])
    r=Elevation(m,"B_stair_return","east",-315.7)
    r.band(506.56,512.14,0,15.72,[])
    e=Elevation(m,"B_courtyard","west",-296.35)
    e.facade(502.,512.16,15.03,[(504.04,1.53),(507.29,1.55),(510.54,1.53)])
