import bpy, math, os
from mathutils import Vector
from math import sin, cos, pi

# TOPSAN globe emblem — procedural Blender scene
OUT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.path.expanduser('~')
BLEND_OUT = os.path.join(OUT_DIR, 'topsan_3d.blend')
GLB_OUT = os.path.join(OUT_DIR, 'topsan_3d.glb')
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.curves, bpy.data.meshes, bpy.data.materials):
    pass

# Materials
def metal(name, color, metallic=0.82, rough=0.24):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metallic; bs.inputs['Roughness'].default_value=rough
    return m
silver=metal('Brushed silver | globe frame',(0.63,0.66,0.69),0.88,0.23)
bright=metal('Polished silver | lettering',(0.82,0.84,0.86),0.92,0.18)
inner=metal('Dark steel | bevel accents',(0.20,0.22,0.24),0.8,0.28)

RX, RY, RZ = 4.55, 1.18, 2.52

def tube(name, points, radius, material, cyclic=False, resolution=10):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=24
    cu.bevel_depth=radius; cu.bevel_resolution=resolution
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points): p.co=(*co,1)
    sp.use_cyclic_u=cyclic
    ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob); ob.data.materials.append(material)
    return ob

# Outer ellipsoid silhouette, with subtly doubled rim as in the reference
for offset,rad in [(0,0.045),(0.035,0.018)]:
    pts=[]
    for i in range(240):
        t=2*pi*i/240
        pts.append(((RX+offset)*cos(t),0,(RZ+offset*0.55)*sin(t)))
    tube('Elliptical outer rim',pts,rad,silver,True,12)

# Meridians: front/back symmetrical longitudinal arcs on an ellipsoid
for lon_deg in [-78,-58,-38,-19,0,19,38,58,78]:
    lam=math.radians(lon_deg); pts=[]
    for i in range(161):
        lat=-pi/2 + pi*i/160
        x=RX*cos(lat)*sin(lam)
        z=RZ*sin(lat)
        y=-RY*cos(lat)*cos(lam)
        pts.append((x,y,z))
    tube(f'Meridian {lon_deg:+d}',pts,0.034 if lon_deg else 0.042,silver,False,8)

# Latitude rings
for lat_deg in [-68,-43,-20,20,43,68]:
    lat=math.radians(lat_deg); pts=[]
    for i in range(240):
        t=2*pi*i/240
        pts.append((RX*cos(lat)*cos(t),-RY*cos(lat)*sin(t),RZ*sin(lat)))
    tube(f'Parallel {lat_deg:+d}',pts,0.034,silver,True,8)

# Slightly stronger equatorial line
pts=[]
for i in range(240):
    t=2*pi*i/240; pts.append((RX*cos(t),-RY*sin(t),0))
tube('Equator',pts,0.038,silver,True,8)

# Lettering as genuinely extruded 3D text. Front faces toward -Y.
font_candidates=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/lato/Lato-Medium.ttf']
font_path=next((p for p in font_candidates if os.path.exists(p)),None)
font=bpy.data.fonts.load(font_path) if font_path else bpy.data.fonts.get('Bfont')
cu=bpy.data.curves.new('TOPSAN dimensional lettering','FONT'); cu.body='topsan'; cu.font=font
cu.size=1.72; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=0.085; cu.bevel_depth=0.025; cu.bevel_resolution=5
ob=bpy.data.objects.new('topsan | solid extruded lettering',cu); bpy.context.collection.objects.link(ob)
ob.location=(0,-1.24,0.02); ob.rotation_euler=(pi/2,0,0); ob.data.materials.append(bright)

# Small dark backing-free bevel accent on lettering is supplied by physical bevel/extrusion.
# Scene setup
world=bpy.context.scene.world
if world is None: world=bpy.data.worlds.new('Studio World'); bpy.context.scene.world=world
world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(0.018,0.018,0.018,1)
world.node_tree.nodes['Background'].inputs[1].default_value=0.35

# Studio lights
for name,loc,power,size,color in [
 ('Key softbox',(-5,-7,6),1500,5,(0.82,0.88,1.0)),
 ('Fill softbox',(5,-4,1),1050,4,(1.0,0.92,0.82)),
 ('Rim light',(0,3,5),1800,3,(0.75,0.84,1.0))]:
    bpy.ops.object.light_add(type='AREA', location=loc); l=bpy.context.object; l.name=name; l.data.energy=power; l.data.shape='DISK'; l.data.size=size; l.data.color=color
    l.rotation_euler=(Vector((0,0,0))-l.location).to_track_quat('-Z','Y').to_euler()

# Camera front view
bpy.ops.object.camera_add(location=(0,-13.5,0.15)); cam=bpy.context.object; cam.name='Front presentation camera'
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=52
scene=bpy.context.scene; scene.camera=cam
# Compatible with Blender 4.0+ and newer releases.
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    scene.render.engine = 'BLENDER_EEVEE'
try:
    scene.eevee.taa_render_samples = 64
except (AttributeError, TypeError):
    pass
scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=True
scene.view_settings.view_transform='AgX'

# Origin at emblem center, useful for orbiting. Save native file and export glTF.
for obj in bpy.context.scene.objects:
    if obj.type in {'MESH','CURVE','FONT'}:
        obj.select_set(True)
    else: obj.select_set(False)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
# Fail the CI job clearly if the glTF exporter is unavailable or export fails.
if not hasattr(bpy.ops, 'export_scene') or not hasattr(bpy.ops.export_scene, 'gltf'):
    raise RuntimeError('Blender glTF exporter is unavailable')
bpy.ops.export_scene.gltf(filepath=GLB_OUT, export_format='GLB', export_apply=True)
if not os.path.isfile(GLB_OUT) or os.path.getsize(GLB_OUT) < 1024:
    raise RuntimeError('GLB export failed or produced an empty file')
print('SUCCESS: created', BLEND_OUT, 'and', GLB_OUT)
