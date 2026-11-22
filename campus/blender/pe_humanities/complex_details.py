"""Shared roofs and the covered crossing as seen from the east courtyard."""
from math import cos, pi, sin, tau
from random import Random


def roof_room(m, x, z, base, width, depth, height):
    """Brick stair enclosure with a raised coping and a recessed service door."""
    top = base + height
    m.box("stair_enclosure", "brick", (x, z, (base+top)/2), (width, depth, height))
    m.box("access_roof", "tile", (x, z, top+.045), (width, depth, .09))
    for edge in (-1, 1):
        m.box("coping", "steel", (x+edge*width/2, z, top+.11), (.13, depth+.13, .22))
        m.box("coping", "steel", (x, z+edge*depth/2, top+.11), (width, .13, .22))
    door_height = min(1.95, height-.12)
    m.box("door_reveal", "metal", (x+width*.22, z+depth/2+.02, base+door_height/2),
          (.91, .06, door_height))
    m.box("roof_door", "steel", (x+width*.22, z+depth/2+.055, base+door_height/2),
          (.78, .05, door_height-.09))
    m.box("door_hood", "ivory", (x+width*.22, z+depth/2+.19, base+door_height+.04),
          (1.09, .43, .09))


def roofs(m):
    # The two oblong roof rooms belong to A. Its east notch is open to the sky.
    m.material("roof_flashing","#868985",.61,.27)
    m.material("roof","#c2bdb3",.94)
    m.image_for["roof"]="cb10_roof"
    # Discontinuous outlines preserve the open terraces and the rounded end.
    def coping(x0,z0,x1,z1,h):
        m.beam("flashing","roof_flashing",(x0,z0,h),(x1,z1,h),.15,.16)
    for x0,z0,x1,z1,h in (
            (-337.94,561.57,-279.87,561.57,4.29),(-337.94,567.08,-279.87,567.08,4.29),
            (-337.94,561.57,-337.94,567.08,4.29),(-279.87,561.57,-279.87,567.08,4.29),
            (-337.91,551.96,-279.90,551.96,16.01),(-337.91,541.28,-337.91,551.96,16.01),
            (-337.91,541.28,-293.06,541.28,16.01),(-324.52,529.64,-321.58,529.64,15.34),
            (-321.58,529.68,-296.31,529.68,14.99),(-296.31,529.76,-287.30,529.76,15.22),
            (-287.31,529.76,-287.31,502.00,15.22),(-296.38,512.13,-296.38,502.00,15.22),
            (-321.57,512.13,-296.38,512.13,14.99)):
        coping(x0,z0,x1,z1,h)
    for i in range(24):
        a,b=pi+pi*i/24,pi+pi*(i+1)/24
        coping(-291.85+4.51*cos(a),502+4.51*sin(a),-291.85+4.51*cos(b),502+4.51*sin(b),15.22)
    roof_room(m, -330.1, 543.55, 15.95, 14.1, 3.95, 1.65)
    roof_room(m, -289.9, 549.12, 15.95, 7.9, 4.15, 1.75)
    roof_room(m, -318.25, 509.0, 15.79, 4.7, 3.4, 2.50)
    roof_room(m, -292.0, 504.8, 15.09, 4.1, 3.35, 2.15)
    roof_room(m, -318.43, 518.22, 14.87, 2.45, 2.70, 1.23)
    m.material("condenser_fins", "#484e4d", .77, .12)
    m.material("equipment_enamel", "#c4c4b8", .55, .16)
    for start_x, start_z, rows in [(-312.0, 519.45, 3), (-319.1, 522.12, 1)]:
        for i in range(2):
            for j in range(rows):
                x, z = start_x+i*1.68, start_z+j*1.87
                for dx in (-.49,.49):
                    m.box("equipment_runner", "metal", (x+dx,z,15.03), (.14,1.78,.31))
                m.box("condenser_shell", "equipment_enamel", (x,z,15.80),(1.56,1.72,1.25))
                m.box("heat_exchanger", "condenser_fins", (x+.788,z,15.79),(.024,1.47,.96))
                for k in range(7):
                    m.box("grille_louver", "steel",(x+.81,z,15.38+k*.133),(.05,1.50,.031))
                # A round axial fan and grille are legible from the overhead view.
                fan = [(x+.57*cos(t*tau/20), z+.57*sin(t*tau/20)) for t in range(20)]
                m.prism("fan_well", "condenser_fins", fan,16.419,16.458)
                for k in range(7):
                    offset = (k-3)*.149
                    chord = 2*(.55**2-offset**2)**.5
                    m.box("fan_grille","steel",(x+offset,z,16.471),(.031,chord,.023))
    for x, z in ((-309.54,525.17), (-305.18,525.17)):
        m.box("sleeper","concrete",(x,z,14.99),(1.63,1.71,.24))
        m.box("plant_housing","equipment_enamel",(x,z,15.75),(1.48,1.53,1.36))
    m.box("duct","steel",(-307.36,525.17,15.41),(3.1,.53,.47))
    for x in (-308.19,-307.31,-306.43):
        m.box("duct_seam","metal",(x,525.17,15.41),(.036,.55,.49))


def west_link(m):
    """The shorter of the two links across the A–B strip, visible in plan."""
    x, z = -320.82, 535.52
    width, depth = 5.15, 11.72
    for h, thickness in ((4.30,.30),(8.52,.18)):
        m.box("west_walkway_slab", "concrete", (x,z,h),(width,depth,thickness))
    m.solid_box((x,z,6.42),(width,depth,4.54))
    for dx in (-width/2,width/2):
        m.box("west_link_glass","bridge_glass",(x+dx,z,6.41),(.07,depth,3.98))
        for j in range(8):
            m.box("west_link_mullion","metal",(x+dx,z-depth/2+j*depth/7,6.44),(.106,.058,4.08))
        m.box("west_link_transom","metal",(x+dx,z,6.7),(.11,depth,.066))
    m.box("west_roof_glazing","glass",(x,z,8.634),(width-.10,depth-.12,.053))
    for j in range(8):
        m.box("roof_glazing_cap","steel",(x,z-depth/2+j*depth/7,8.683),(width,.063,.045))
    for dx in (-width/2,0,width/2):
        m.box("roof_glazing_cap","steel",(x+dx,z,8.683),(.063,depth,.045))
    # The higher, eastern bridge also has a capped glazed roof.
    for j in range(6):
        for i in range(4):
            m.box("east bridge roof lights","glass",(-295.64+(i+.5)*1.85,529.62+(j+.5)*1.97,11.689),
                  (1.79,1.91,.035))


def east_forecourt(m):
    # Connect the flush courtyard paving to the west edge of the existing
    # 4.8 m campus road (centreline x=-271.19). Flare the two kerb returns.
    m.material("apron_granite", "#b9b3a6", .91)
    m.material("kerb_granite", "#aaa79e", .92)
    stations = [(-278.68,554.18,560.77,.052), (-277.55,554.17,560.78,.060),
                (-276.2,554.07,560.88,.075), (-275.24,553.84,561.11,.087),
                (-274.38,553.43,561.52,.095), (-273.56,552.83,562.12,.104)]
    for (x0,n0,s0,h0),(x1,n1,s1,h1) in zip(stations,stations[1:]):
        outline=[(x0,n0),(x1,n1),(x1,s1),(x0,s0)]
        m.face("apron_granite",[(x0,n0,h0),(x1,n1,h1),(x1,s1,h1),(x0,s0,h0)])
        m.solid(outline,-.20,(h0+h1)*.5)
        # Kerbs are broken at the roadway and at the gate, leaving a level crossing.
        for a,b,direction in ((n0,n1,-1),(s0,s1,1)):
            kerb=[(x0,a),(x1,b),(x1,b+direction*.18),(x0,a+direction*.18)]
            m.prism("kerb","kerb_granite",kerb,h0-.04,h1+.10)
    for n in range(8):
        x=-278.4+n*.63
        h=.055+(x+278.68)*.0095
        m.box("paving joint","court_joints",(x,557.47,h+.002),(.012,6.35,.005))
    # Recessed drainage across the entrance, outside the historic plaque columns.
    m.box("drain frame","metal",(-278.55,557.47,.059),(.14,6.35,.014))
    for n in range(48):
        m.box("drain bar","steel",(-278.55,554.37+n*.132,.069),(.12,.047,.012))

    # An open, paved turning bay wraps under the oriel into the covered lane.
    turn=[(-293.00,535.0),(-284.4,535.0),(-279.0,539.6),(-276.15,541.4),
          (-276.15,544.36),(-279.0,546.18),(-293.00,546.18)]
    m.prism("oriel forecourt","curb_asphalt",turn,-.018,.041)
    m.solid(turn,-.19,.041)
    # The west exit opens into a small daylight court in front of the adjacent
    # campus building. Its existing windows are visible at the end of the lane.
    rear=[(-337.6,529.7),(-331.8,529.7),(-323.84,532.32),(-323.84,538.77),
          (-331.4,541.15),(-337.6,541.15)]
    m.prism("west court","apron_granite",rear,-.025,.052)
    m.solid(rear,-.19,.052)
    for z in (532.4,538.72):
        m.box("west court gutter","steel",(-330.8,z,.057),(8.3,.115,.018))


def parked_scooter(m, cx, cz, yaw, paint):
    """A step-through campus e-bike in its parking bay; coordinates are axle-aligned."""
    c, s = cos(yaw), sin(yaw)
    def point(u,v,h):
        return (cx+c*u-s*v, cz+s*u+c*v, h)
    def beam(name,mat,p,q,width):
        m.beam(name,mat,point(*p),point(*q),width)
    def body(name,mat,profile,width):
        # Extruded side profile in the scooter's longitudinal vertical plane.
        near=[point(u,-width/2,h) for u,h in profile]
        far=[point(u,width/2,h) for u,h in profile]
        m.face(mat,near)
        m.face(mat,far[::-1])
        for i in range(len(near)):
            j=(i+1)%len(near)
            m.face(mat,[near[i],far[i],far[j],near[j]])
    for u in (-.51,.55):
        # Open wheel centre and narrow metal spokes survive the oblique views.
        for j in range(12):
            angles=[tau*j/12,tau*(j+1)/12]
            for v,other in ((-.051,.051),(.051,-.051)):
                arc=[point(u+.22*cos(a),v,.257+.22*sin(a)) for a in angles]
                inner=[point(u+.151*cos(a),v,.257+.151*sin(a)) for a in angles]
                points=arc+inner[::-1]
                m.face("rubber",points if v<0 else points[::-1])
                if v<0:
                    outer=[point(u+.22*cos(a),other,.257+.22*sin(a)) for a in angles]
                    m.face("rubber",[arc[1],arc[0],outer[0],outer[1]])
            if j%2==0:
                beam("spoke","steel",(u,0,.257),(u+.166*cos(angles[0]),0,.257+.166*sin(angles[0])),.025)
    body("rear fairing",paint,[(-.76,.37),(-.27,.34),(-.04,.43),(-.12,.65),(-.55,.72),(-.79,.58)],.31)
    body("saddle","rubber",[(-.66,.68),(-.13,.65),(-.08,.71),(-.17,.78),(-.63,.79),(-.72,.74)],.31)
    m.box("footboard","rubber",point(.08,0,.315),(.50,.31,.078),yaw)
    body("front apron","cream",[(.25,.30),(.38,.31),(.57,.77),(.50,.89),(.40,.84)],.23)
    for v in (-.079,.079):
        beam("fork","steel",(.55,v,.257),(.48,v,.79),.047)
    beam("steering stem","metal",(.47,0,.73),(.41,0,1.03),.047)
    beam("grips","rubber",(.40,-.265,1.03),(.40,.265,1.03),.048)
    beam("mirror stem","steel",(.40,.17,1.03),(.43,.24,1.19),.022)
    m.box("mirror","metal",point(.43,.24,1.19),(.057,.11,.075),yaw)
    m.box("headlamp","ivory",point(.54,0,.87),(.07,.13,.071),yaw)


def passage(m):
    m.material("curb_asphalt", "#747579", .94)
    m.material("rubber","#2c2c2d",.90)
    m.material("passage_ceiling", "#49494a", .92)
    m.material("lamp_diffuser","#f1e9ca",.55)
    m.materials["lamp_diffuser"]["emissiveFactor"]=[.40,.38,.29]
    # Exposed concrete frames, darker soffit, longitudinal central rib and lights
    # continue west from the glass bridge. Maintain a clear lane at ground level.
    start, end, z = -323.8, -288.1, 535.525
    m.box("underside lining","passage_ceiling",((start+end)/2,z,4.09),(end-start,5.72,.035))
    m.box("spine beam","concrete",((start+end)/2,z,4.00),(end-start,.18,.14))
    # Brick and recessed windows on both sides of the long covered section.
    # Leave the ends and intermediate cross passages open.
    for side in (-1,1):
        wall_z=z+side*2.94
        for x in (-319.6,-315.1,-306.0,-301.5):
            for delta in (-1.65,1.65):
                m.box("brick jamb","brick",(x+delta,wall_z,1.98),(.92,.22,3.96))
            m.box("infill sill","brick",(x,wall_z,.45),(2.42,.22,.90))
            m.box("infill head","brick",(x,wall_z,3.67),(2.42,.22,.58))
            m.box("concrete lintel","concrete",(x,wall_z-side*.085,3.40),(2.5,.18,.16))
            m.box("window frame","metal",(x,wall_z+side*.045,2.10),(2.42,.09,2.41))
            for dx in (-.59,.59):
                m.box("smoked pane","glass_dark",(x+dx,wall_z-side*.015,2.15),(1.10,.031,2.16))
            m.solid_box((x,wall_z,1.98),(4.22,.24,3.96))
    for x in (-320.6,-315.8,-311.1,-306.9,-302.2,-297.7,-293.8,-289.7):
        for side in (-1,1):
            m.box("strip fixture","metal",(x,z+side*1.48,4.047),(.85,.135,.044))
            m.box("linear diffuser","lamp_diffuser",(x,z+side*1.48,4.019),(.77,.077,.018))
    rng=Random(100705)
    def bay(x, z, yaw, floor):
        m.parking.append({"position": [x, floor, z], "rotation_y": pi - yaw})
        m.solid_box((x,z,floor+.46),(1.60,.50,.92),yaw)
    for side,positions in ((-1,[-319.4,-314.0,-312.7,-305.6,-301.2,-296.1,-294.7,-290.7]),
                           (1,[-316.0,-310.8,-309.4,-302.9,-297.8,-292.0])):
        for x in positions:
            y=z+side*(2.12+rng.uniform(-.10,.10))
            yaw=-side*(pi/2+rng.uniform(-.40,.36))
            rng.randrange(5)  # Preserve the original parking layout's random sequence.
            # The easternmost south-side bay overlaps the raised oriel forecourt.
            bay(x, y, yaw, .041 if x == -292.0 else .028)
    for x,z,yaw,floor in [(-283.12,545.5,-.30,.041),(-286.2,545.5,-.39,.041),
                          (-330.3,531.7,-.42,.052),(-331.65,532.0,-.49,.052)]:
        bay(x, z, yaw, floor)
