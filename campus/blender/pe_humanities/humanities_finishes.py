"""Measured-scale surface textures and pane reflections for humanities wings A/C."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


MASONRY = "cb10_fired_clay"
CONCRETE = "cb10_cast_concrete"
ROOF = "cb10_roof_membrane"
GLASS = "cb10_window_glass"
EAST_GLASS = "cb10_east_curtain_glass"
HALL_UPPER = "cb10_hall_upper_glass"
HALL_LOWER = "cb10_hall_lower_glass"
WINDOWS = {GLASS, EAST_GLASS, HALL_UPPER, HALL_LOWER}
FINISH = {"brick": MASONRY, "concrete": CONCRETE, "roof": ROOF}
REPEAT_METRES = {MASONRY: (2.88, 2.08), ROOF: (4.8, 3.2), "court_stone": (4.88, 2.96)}


def rgb(data):
    return Image.fromarray(np.clip(np.rint(data), 0, 255).astype(np.uint8))


def masonry():
    # Twelve 240 mm stretchers and thirty-two 65 mm courses, including joints.
    rng = np.random.default_rng(710)
    y, x = np.mgrid[:512, :768]
    row = y // 16
    bed = (y + .37 * np.sin(x * np.pi / 24) + .22 * np.cos(x * np.pi / 32) + .5) % 16
    shifted = x + (row % 2) * 32
    col = (shifted // 64) % 12
    head = (shifted + .34 * np.sin(y * np.pi / 8) + .5) % 64
    dist = np.minimum(np.minimum(bed, 16-bed), np.minimum(head, 64-head))
    face = np.clip((dist-.70)/1.05, 0, 1)
    kiln = rng.normal(0, 4.0, (32, 12))[row, col]
    fired = rng.normal(0, 2.6, (32, 12))[row, col]
    grain = rng.normal(0, 2.6, x.shape)
    cloud = 1.8*np.cos(np.pi*x/96)*np.cos(np.pi*y/64) + 1.5*np.sin(np.pi*x/32 + np.pi*y/16)
    clay = np.array([153, 86, 65]) + (kiln + grain + cloud)[..., None]
    clay += fired[..., None] * [1.0, .18, -.35]
    grout = np.array([153, 130, 113]) + grain[..., None] * .72
    albedo = rgb(grout + face[..., None]*(clay-grout))
    # glTF tangent space uses +Y up. Image rows increase downwards.
    height = face * 1.25
    dx = (np.roll(height, -1, axis=1)-np.roll(height, 1, axis=1)) * .5
    dy = (np.roll(height, -1, axis=0)-np.roll(height, 1, axis=0)) * .5
    normal = np.stack((-dx, dy, np.ones_like(dx)), axis=-1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    return albedo, rgb(127.5*(normal+1))


def mineral_textures():
    rng = np.random.default_rng(471)
    y, x = np.mgrid[:384, :384]
    fine = rng.normal(0, 3.2, x.shape)
    cloud = 1.9*np.sin(x*np.pi/96)*np.cos(y*np.pi/48) + 1.4*np.cos((x+y)*np.pi/32)
    # A neutral aggregate map lets both the brown-grey lintels and pale granite
    # use their own colour factors instead of adding a material for each piece.
    mineral = rgb(244 + fine + cloud - rng.binomial(1, .024, x.shape)*12).convert("L")
    roll = (x + (y//192)*96) % 192
    laps = (roll < 2) | (y % 192 < 2)
    roof = rgb(239 + fine*.67 + cloud*1.5 - laps*24).convert("L")
    # Four by four slabs share the existing courtyard joint centres.
    stones = rng.uniform(-4, 4, (4, 4))[y//96, x//96]
    stone = rgb(242 + fine*1.4 + cloud + stones).convert("L")
    return mineral, roof, stone


def quadrilateral(photo, vertices, size):
    # Pillow QUAD takes top-left, bottom-left, bottom-right, top-right.
    return photo.transform(size, Image.Transform.QUAD,
                          tuple(value for point in vertices for value in point),
                          resample=Image.Resampling.BICUBIC)


def curtain(photo, corners, panes, cuts):
    """Rectify the reflection only. The model supplies its own metal frame."""
    tl, bl, br, tr = np.asarray(corners, dtype=float)

    def point(u, v):
        return (1-v)*((1-u)*tl + u*tr) + v*((1-u)*bl + u*br)

    width, height = 512, 256
    image = Image.new("RGB", (width, height))
    for i in range(panes):
        left, right = round(width*i/panes), round(width*(i+1)/panes)
        for top, bottom in zip(cuts, cuts[1:]):
            y0, y1 = round(height*top), round(height*bottom)
            # The oblique view makes adjacent panes unequal in the photo.
            # Stay clear of the frame even in the widest pane.
            a, b = (i+.16)/panes, (i+.84)/panes
            c, d = top+.026, bottom-.026
            patch = quadrilateral(photo, [point(a,c), point(a,d), point(b,d), point(b,c)],
                                  (right-left, y1-y0))
            image.paste(patch, (left, y0))
    return image.filter(ImageFilter.GaussianBlur(1.1))


def window_atlas(classroom, link, south):
    # Samples lie inside the glazing. No people, signs or foreground objects
    # are projected onto the windows. Lighting and specular still run in-game.
    with Image.open(classroom) as photo:
        samples = [
            quadrilateral(photo, points, (192, 192)) for points in [
                [(713,1026), (707,1268), (878,1264), (879,1020)],
                [(1345,995), (1352,1258), (1509,1259), (1507,991)],
                [(2223,955), (2231,1245), (2511,1248), (2507,937)],
            ]
        ]
    with Image.open(link) as photo:
        samples.append(quadrilateral(photo, [(1141,1658),(1124,1933),(1279,1943),(1291,1665)], (192,192)))
    # Upper storeys mainly reflect the sky. Take two additional reflections
    # from clear panes in A's south facade, outside the sash and lettering.
    with Image.open(south) as photo:
        for points in [
            [(1600,886),(1601,1074),(1694,1031),(1693,837)],
            [(1324,1041),(1325,1188),(1365,1168),(1366,1013)],
        ]:
            samples.append(quadrilateral(photo, points, (192,192)))
    atlas = Image.new("RGB", (3*208, 2*208))
    for i, sample in enumerate(samples):
        # Lower contrast retains the broad shape of the reflected buildings.
        # An eight-pixel gutter keeps neighbouring rooms out of the mip levels.
        sample = ImageEnhance.Contrast(sample.convert("RGB")).enhance(.70)
        extended = np.pad(np.asarray(sample), ((8,8),(8,8),(0,0)), mode="edge")
        atlas.paste(Image.fromarray(extended), ((i%3)*208,(i//3)*208))
    return atlas


def east_glazing(path):
    with Image.open(path) as photo:
        return curtain(photo, [(1448,831),(1467,1617),(1984,1698),(1906,938)], 3, [0,.12,.47,.60,1])


def hall_glazing(path):
    with Image.open(path) as photo:
        return curtain(photo, [(610,619),(548,1211),(1762,1287),(1770,677)], 6, [0,.56,1])


def reflection_textures(campus):
    relative = Path("建筑/CB10_新人文楼／人文与社会科学学院/照片")
    archives = [campus.parent/"data"/relative, campus/"references/Photographic_data"/relative]
    bundled = Path(__file__).with_name("textures")
    link = "新人文楼-A楼C楼连接处-东侧.png"
    recipes = [
        ("cb10_panes", window_atlas, ("新人文楼C楼-C101-北侧.png", link, "新人文楼-A楼-南侧.jpg")),
        ("cb10_east_glazing", east_glazing, ("新人文楼-A楼-东侧.png",)),
        ("cb10_hall_glazing", hall_glazing, (link,)),
    ]
    textures = {}
    for key, extract, names in recipes:
        paths = [next((a/name for a in archives if (a/name).is_file()), None) for name in names]
        if all(paths):
            textures[key] = extract(*paths)
        else:
            with Image.open(bundled/(key+".png")) as crop:
                textures[key] = crop.convert("RGB")
    return textures


def install(model, campus):
    clay, normal = masonry()
    aggregate, roof, paving = mineral_textures()
    model.textures.update(cb10_clay=clay, cb10_clay_normal=normal, cb10_aggregate=aggregate,
                          cb10_roof=roof, cb10_paving=paving)
    model.textures.update(reflection_textures(campus))
    model.jpeg_images.update(("cb10_clay", "cb10_aggregate", "cb10_roof", "cb10_paving",
                              "cb10_panes", "cb10_east_glazing", "cb10_hall_glazing"))
    model.material(MASONRY, "#ffffff", .88)
    model.material(CONCRETE, "#b5b0a2", .85)
    model.material(ROOF, "#c2bdb3", .94)
    model.material(GLASS, "#c4c8c8", .19, .29)
    model.material(EAST_GLASS, "#cad4d6", .14, .34)
    model.image_for.update({MASONRY:"cb10_clay", CONCRETE:"cb10_aggregate", ROOF:"cb10_roof",
                            GLASS:"cb10_panes", EAST_GLASS:"cb10_east_glazing",
                            HALL_UPPER:"cb10_hall_glazing", HALL_LOWER:"cb10_panes",
                            "humanities_sill":"cb10_aggregate", "court_stone":"cb10_paving"})
    model.normal_for[MASONRY] = ("cb10_clay_normal", .52)


def pane_material(model, name, mat):
    if mat == "hall_glass":
        key = HALL_UPPER if "Upper" in name else HALL_LOWER
        if key not in model.materials:
            source = model.materials[mat]
            pbr = source["pbrMetallicRoughness"].copy()
            # Reflection hue comes from the photograph. Keep the architect's
            # glass transparency and response to the environment on both floors.
            pbr["baseColorFactor"] = [.85, .89, .93, pbr["baseColorFactor"][3]]
            model.materials[key] = {**source, "name":key, "pbrMetallicRoughness":pbr}
        return key
    if mat in {"glass", "glass_dark"}:
        return EAST_GLASS if "GlazedBay" in name else GLASS
    return mat


def pane_uv(points, mat, center):
    p = np.asarray(points, dtype=float)
    normal = np.cross(p[1]-p[0], p[2]-p[0])
    horizontal = p[:,:2] @ [normal[1], -normal[0]]
    u = (horizontal-horizontal.min()) / max(np.ptp(horizontal), 1.e-8)
    v = (p[:,2].max()-p[:,2]) / max(np.ptp(p[:,2]), 1.e-8)
    if mat in (GLASS, HALL_LOWER):
        # A given bay's two sides share a room. Vary adjacent bays and floors.
        x, y, z = center
        index = (round(x*3) + round(y*2) + round(z)) % 4
        if z > 3.9:
            index = 4 + index%2
        u = ((index%3)*208 + 8.5 + 191*u) / 624
        v = ((index//3)*208 + 8.5 + 191*v) / 416
    return np.column_stack((u,v))
