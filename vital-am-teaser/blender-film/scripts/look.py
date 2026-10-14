# Look-dev: materials, sky/sun, water volume, ground & treeline, compositor. Opens film_base.blend -> film.blend
import bpy, math, random, sys
from mathutils import Vector, Matrix
S='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/'
bpy.ops.wm.open_mainfile(filepath=S+'film/film_base.blend')
sc=bpy.context.scene; random.seed(11)
for n in ('HERO_VitalAM_Bag_10kg','ENV_Sun_Disc'):
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o)
def nm(name):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); b=nt.nodes.new('ShaderNodeBsdfPrincipled'); nt.links.new(b.outputs[0],out.inputs[0])
    return m,nt.nodes,nt.links,b,out
def noise(n,l,scale,detail=6,rough=0.55,coord=None):
    t=n.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value=scale; t.inputs['Detail'].default_value=detail; t.inputs['Roughness'].default_value=rough
    if coord is not None: l.new(coord,t.inputs['Vector'])
    return t
def ramp(n,l,src,c0,c1,p0=0.0,p1=1.0):
    r=n.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color=(*c0,1); r.color_ramp.elements[1].color=(*c1,1)
    r.color_ramp.elements[0].position=p0; r.color_ramp.elements[1].position=p1; l.new(src,r.inputs[0]); return r
def bump(n,l,src,b,strength=0.3,dist=0.02):
    bp=n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=strength; bp.inputs['Distance'].default_value=dist; l.new(src,bp.inputs['Height']); l.new(bp.outputs[0],b.inputs['Normal']); return bp
def gcoord(n): return n.new('ShaderNodeTexCoord')
# ---- water surface: clear, slightly green, rippled; lets the camera see into the volume below
m,n,l,b,out=nm('MAT_Pond_Water_Surface')
b.inputs['Base Color'].default_value=(0.20,0.30,0.18,1); b.inputs['Transmission Weight'].default_value=1.0; b.inputs['Roughness'].default_value=0.03; b.inputs['IOR'].default_value=1.333
tc=gcoord(n); mp=n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(1.0,2.6,1.0); l.new(tc.outputs['Object'],mp.inputs[0])
n1=noise(n,l,1.6,8,0.6,mp.outputs[0]); n2=noise(n,l,14,4,0.5,mp.outputs[0]); ad=n.new('ShaderNodeMath'); ad.operation='MULTIPLY_ADD'; ad.inputs[1].default_value=0.35
l.new(n2.outputs['Fac'],ad.inputs[0]); l.new(n1.outputs['Fac'],ad.inputs[2]); bump(n,l,ad.outputs[0],b,0.22,0.015)
lp=n.new('ShaderNodeLightPath'); tr=n.new('ShaderNodeBsdfTransparent'); mxs=n.new('ShaderNodeMixShader')
mxa=n.new('ShaderNodeMath'); mxa.operation='MAXIMUM'; l.new(lp.outputs['Is Camera Ray'],mxa.inputs[0]); l.new(lp.outputs['Is Glossy Ray'],mxa.inputs[1])
# from above, turbid pond water: part of the glass is replaced by a murky green body colour (front faces only)
geo2=n.new('ShaderNodeNewGeometry'); turb=n.new('ShaderNodeBsdfDiffuse'); turb.inputs['Color'].default_value=(0.11,0.15,0.065,1)
fm=n.new('ShaderNodeMath'); fm.operation='MULTIPLY'; fm.inputs[1].default_value=0.0; inv=n.new('ShaderNodeMath'); inv.operation='SUBTRACT'; inv.inputs[0].default_value=1.0
l.new(geo2.outputs['Backfacing'],inv.inputs[1]); l.new(inv.outputs[0],fm.inputs[0]); fm.inputs[1].default_value=1.0
fr2=n.new('ShaderNodeFresnel'); fr2.inputs['IOR'].default_value=1.333; fm2=n.new('ShaderNodeMath'); fm2.operation='MULTIPLY'; l.new(fm.outputs[0],fm2.inputs[0]); inv2=n.new('ShaderNodeMath'); inv2.operation='SUBTRACT'; inv2.inputs[0].default_value=1.0; l.new(fr2.outputs[0],inv2.inputs[1]); l.new(inv2.outputs[0],fm2.inputs[1])
mxt=n.new('ShaderNodeMixShader'); l.new(fm2.outputs[0],mxt.inputs[0]); l.new(b.outputs[0],mxt.inputs[1]); l.new(turb.outputs[0],mxt.inputs[2])
l.new(mxa.outputs[0],mxs.inputs[0]); l.new(tr.outputs[0],mxs.inputs[1]); l.new(mxt.outputs[0],mxs.inputs[2]); l.new(mxs.outputs[0],out.inputs[0])
ws=bpy.data.objects['POND_Water_Surface']; ws.visible_shadow=False
# ---- water volume (turbid green pond water) filling the ponds
bpy.ops.mesh.primitive_cube_add(location=(0,0,-0.805)); vol=bpy.context.object; vol.name='WATER_VOLUME'; vol.scale=(66,51,0.8)
mv=bpy.data.materials.new('MAT_WaterVolume'); mv.use_nodes=True; nt=mv.node_tree; nt.nodes.clear(); o2=nt.nodes.new('ShaderNodeOutputMaterial')
pv=nt.nodes.new('ShaderNodeVolumePrincipled'); pv.inputs['Color'].default_value=(0.32,0.62,0.56,1); pv.inputs['Density'].default_value=0.22
pv.inputs['Anisotropy'].default_value=0.7; pv.inputs['Absorption Color'].default_value=(0.30,0.62,0.52,1); nt.links.new(pv.outputs[0],o2.inputs['Volume']); vol.data.materials.append(mv)
vol.visible_shadow=False
# ---- basin: earthen dykes above the waterline, black HDPE liner on the slopes, soft mud on the floor
m,n,l,b,out=nm('MAT_HDPE_Liner')
geo=n.new('ShaderNodeNewGeometry'); sep=n.new('ShaderNodeSeparateXYZ'); l.new(geo.outputs['Position'],sep.inputs[0])
mr=n.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=-1.35; mr.inputs['From Max'].default_value=-1.05; l.new(sep.outputs['Z'],mr.inputs['Value'])
nz=noise(n,l,3.0,8)
mud=ramp(n,l,nz.outputs['Fac'],(0.10,0.09,0.05),(0.21,0.19,0.11),0.35,0.75)
mix=n.new('ShaderNodeMix'); mix.data_type='RGBA'; l.new(mr.outputs[0],mix.inputs['Factor']); l.new(mud.outputs[0],mix.inputs['A']); mix.inputs['B'].default_value=(0.035,0.037,0.035,1)
l.new(mix.outputs['Result'],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.55; bump(n,l,nz.outputs['Fac'],b,0.15,0.02)
m,n,l,b,out=nm('MAT_Dyke_Earth')
tc=gcoord(n); nz=noise(n,l,0.6,10,0.6,tc.outputs['Object']); nz2=noise(n,l,9,6,0.6,tc.outputs['Object'])
grass=ramp(n,l,nz.outputs['Fac'],(0.13,0.16,0.05),(0.30,0.33,0.10),0.35,0.7)
earth=ramp(n,l,nz2.outputs['Fac'],(0.22,0.15,0.08),(0.36,0.27,0.16))
mx=n.new('ShaderNodeMix'); mx.data_type='RGBA'; fr=ramp(n,l,nz2.outputs['Fac'],(0,0,0),(1,1,1),0.42,0.62); l.new(fr.outputs[0],mx.inputs['Factor'])
l.new(earth.outputs[0],mx.inputs['A']); l.new(grass.outputs[0],mx.inputs['B']); l.new(mx.outputs['Result'],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.95
bump(n,l,nz2.outputs['Fac'],b,0.4,0.03)
m,n,l,b,out=nm('MAT_Silt_Patch'); b.inputs['Base Color'].default_value=(0.09,0.08,0.045,1); b.inputs['Roughness'].default_value=1
# ---- wood (dock, pallet, shed, room furniture)
def wood(name,c0,c1,scale=(1,9,1),rough=0.75):
    m,n,l,b,out=nm(name); tc=gcoord(n); mp=n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=scale; l.new(tc.outputs['Object'],mp.inputs[0])
    wv=n.new('ShaderNodeTexWave'); wv.wave_type='BANDS'; wv.inputs['Scale'].default_value=3.0; wv.inputs['Distortion'].default_value=7; wv.inputs['Detail'].default_value=8; l.new(mp.outputs[0],wv.inputs[0])
    r=ramp(n,l,wv.outputs['Fac'],c0,c1); l.new(r.outputs[0],b.inputs['Base Color']); b.inputs['Roughness'].default_value=rough; bump(n,l,wv.outputs['Fac'],b,0.12,0.005)
wood('MAT_Walkway_Wood_Weathered',(0.16,0.11,0.07),(0.36,0.27,0.18))
m,n,l,b,out=nm('MAT_Room_Dark_Wood'); nz=noise(n,l,40,8,0.6); r=ramp(n,l,nz.outputs['Fac'],(0.05,0.028,0.016),(0.11,0.065,0.038)); l.new(r.outputs[0],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.35; b.inputs['Coat Weight'].default_value=0.4
wood('MAT_Shed_Wall',(0.20,0.14,0.08),(0.40,0.30,0.18),scale=(1,1,6))
m,n,l,b,out=nm('MAT_Tin_Roof'); tc=gcoord(n); wv=n.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value=25; l.new(tc.outputs['Object'],wv.inputs[0])
nz=noise(n,l,4,8); r=ramp(n,l,nz.outputs['Fac'],(0.30,0.15,0.07),(0.55,0.55,0.56),0.35,0.7); l.new(r.outputs[0],b.inputs['Base Color'])
b.inputs['Metallic'].default_value=0.6; b.inputs['Roughness'].default_value=0.5; bump(n,l,wv.outputs['Fac'],b,0.5,0.02)
# ---- room
m,n,l,b,out=nm('MAT_Room_Wall_Lime'); nz=noise(n,l,8,8); r=ramp(n,l,nz.outputs['Fac'],(0.55,0.56,0.52),(0.70,0.70,0.65)); l.new(r.outputs[0],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.95; bump(n,l,nz.outputs['Fac'],b,0.08)
m,n,l,b,out=nm('MAT_Room_Tile_Floor'); tc=gcoord(n); ck=n.new('ShaderNodeTexBrick'); ck.inputs['Scale'].default_value=3; ck.inputs['Mortar Size'].default_value=0.01
ck.inputs['Color1'].default_value=(0.42,0.30,0.22,1); ck.inputs['Color2'].default_value=(0.48,0.35,0.26,1); ck.inputs['Mortar'].default_value=(0.2,0.18,0.16,1); l.new(tc.outputs['Object'],ck.inputs['Vector']); l.new(ck.outputs['Color'],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.35
m,n,l,b,out=nm('MAT_Bed_Sheet'); b.inputs['Base Color'].default_value=(0.55,0.58,0.62,1); b.inputs['Roughness'].default_value=0.9; b.inputs['Sheen Weight'].default_value=0.5
m,n,l,b,out=nm('MAT_Mosquito_Net'); b.inputs['Base Color'].default_value=(0.9,0.9,0.92,1); b.inputs['Alpha'].default_value=0.18; b.inputs['Roughness'].default_value=0.9
m,n,l,b,out=nm('MAT_Window_Predawn'); b.inputs['Base Color'].default_value=(0,0,0,1); b.inputs['Emission Color'].default_value=(0.38,0.52,0.95,1); b.inputs['Emission Strength'].default_value=2.2
m,n,l,b,out=nm('MAT_Glass_Water'); b.inputs['Transmission Weight'].default_value=1; b.inputs['Roughness'].default_value=0.0
# ---- phone + hand
m,n,l,b,out=nm('MAT_Phone_Body'); b.inputs['Base Color'].default_value=(0.02,0.02,0.025,1); b.inputs['Roughness'].default_value=0.2; b.inputs['Coat Weight'].default_value=1
m,n,l,b,out=nm('MAT_Phone_Screen'); b.inputs['Base Color'].default_value=(0.02,0.05,0.2,1); b.inputs['Roughness'].default_value=0.05; b.inputs['Base Color'].default_value=(0.01,0.06,0.45,1); b.inputs['Emission Color'].default_value=(0.02,0.12,0.9,1); b.inputs['Emission Strength'].default_value=0.7; b.inputs['Coat Weight'].default_value=1
for nmn in ('MAT_Phone_Text','MAT_Phone_Stop_Button'):
    m,n,l,b,out=nm(nmn); b.inputs['Base Color'].default_value=(1,1,1,1); b.inputs['Emission Color'].default_value=(1,1,1,1); b.inputs['Emission Strength'].default_value=2.5
m,n,l,b,out=nm('MAT_Farmer_Skin'); b.inputs['Base Color'].default_value=(0.55,0.36,0.25,1); b.inputs['Subsurface Weight'].default_value=0.35; b.inputs['Subsurface Radius'].default_value=(0.01,0.004,0.002); b.inputs['Roughness'].default_value=0.5
m,n,l,b,out=nm('MAT_Farmer_Sleeve_Cotton'); b.inputs['Base Color'].default_value=(0.24,0.32,0.42,1); b.inputs['Roughness'].default_value=0.9; b.inputs['Sheen Weight'].default_value=0.4
# ---- farmer texture: a touch more saturation so the blue shirt survives the warm dawn light
fb=bpy.data.objects.get('FARMER_BODY')
if fb:
    for m in fb.data.materials:
        nt=m.node_tree; pb=[x for x in nt.nodes if x.type=='BSDF_PRINCIPLED'][0]; lk=pb.inputs['Base Color'].links
        if lk:
            src=lk[0].from_socket; hs=nt.nodes.new('ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value=1.55; hs.inputs['Value'].default_value=1.05
            nt.links.new(src,hs.inputs['Color']); nt.links.new(hs.outputs[0],pb.inputs['Base Color'])
# ---- ground beyond the ponds + distant tree line with palms (instances of the scene palm)
for k,(cx,cy,sx,sy) in enumerate(((0,800,1500,749),(0,-800,1500,749),(800,0,734,51.5),(-800,0,734,51.5))):
    bpy.ops.mesh.primitive_plane_add(size=2,location=(cx,cy,0.795)); g=bpy.context.object; g.name='GROUND_FAR_%d'%k; g.scale=(sx,sy,1)
    g.data.materials.append(bpy.data.materials['MAT_Dyke_Earth'])
palm=bpy.data.objects.get('coconut_palm')
mt,n,l,b,out=nm('MAT_TreeLine'); b.inputs['Base Color'].default_value=(0.06,0.09,0.035,1); b.inputs['Roughness'].default_value=0.9
for i in range(260):
    ang=random.uniform(0,2*math.pi); R=random.uniform(110,240); x,y=math.cos(ang)*R,math.sin(ang)*R*0.9
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=random.uniform(4,9),location=(x,y,0.8+random.uniform(1.5,3.0)))
    t=bpy.context.object; t.scale=(1.5,1.5,0.55); t.data.materials.append(mt); t.name='TREE_%03d'%i
if palm:
    for i in range(70):
        ang=random.uniform(0,2*math.pi); R=random.uniform(80,200)
        q=palm.copy(); sc.collection.objects.link(q); q.name='PALM_FAR_%03d'%i
        s=random.uniform(0.9,1.5); q.matrix_world=Matrix.Translation((math.cos(ang)*R,math.sin(ang)*R*0.9,0.8))@Matrix.Rotation(random.uniform(0,6.3),4,'Z')@Matrix.Scale(s,4)@Matrix.Rotation(math.radians(90),4,'X')
# ---- sky + sun (Nishita sunrise, warm), the direction is set per frame from the previs sun
w=bpy.data.worlds.new('FILM_W'); sc.world=w; w.use_nodes=True; nt=w.node_tree; sk=nt.nodes.new('ShaderNodeTexSky'); sk.name='SKY'; sk.sky_type='NISHITA'
sk.sun_elevation=math.radians(4); sk.altitude=30; sk.air_density=1.4; sk.dust_density=1.6; sk.ozone_density=2.0; sk.sun_intensity=0.12; sk.sun_size=math.radians(1.6)
bg=nt.nodes['Background']; nt.links.new(sk.outputs[0],bg.inputs[0]); bg.inputs[1].default_value=0.27
sd=bpy.data.lights.new('SUN','SUN'); sd.energy=3.2; sd.angle=math.radians(1.2); sd.color=(1.0,0.80,0.62); so=bpy.data.objects.new('SUN',sd); sc.collection.objects.link(so)
# gobo above the water for light shafts (only switched on in underwater frames)
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,0,0.5)); gob=bpy.context.object; gob.name='GOBO'; gob.scale=(140,110,1)
m,n,l,b,out=nm('MAT_Gobo'); tc=gcoord(n); nz=noise(n,l,1.4,3,0.5,tc.outputs['Object']); r=ramp(n,l,nz.outputs['Fac'],(0,0,0),(1,1,1),0.47,0.53); l.new(r.outputs[0],b.inputs['Alpha']); b.inputs['Base Color'].default_value=(0,0,0,1)
gob.data.materials.append(m); gob.visible_camera=False; gob.visible_diffuse=False; gob.visible_glossy=False; gob.visible_transmission=False; gob.visible_volume_scatter=False; gob.hide_render=True
uw=bpy.data.lights.new('UW_FILL','SUN'); uw.energy=0; uw.angle=math.radians(20); uw.color=(0.75,0.95,0.85); uo=bpy.data.objects.new('UW_FILL',uw); sc.collection.objects.link(uo)
# room lights
# window: first dawn light, same warm key as outside
rl=bpy.data.lights.new('ROOM_WIN','AREA'); rl.energy=260; rl.size=1.0; rl.color=(1.0,0.70,0.48); ro=bpy.data.objects.new('ROOM_WIN',rl); sc.collection.objects.link(ro)
ro.location=(100.75,1.45,1.45); ro.rotation_euler=(math.radians(-90),0,0)
pl=bpy.data.lights.new('PHONE_GLOW','POINT'); pl.energy=4.0; pl.shadow_soft_size=0.25; pl.color=(0.35,0.55,1.0); po=bpy.data.objects.new('PHONE_GLOW',pl); sc.collection.objects.link(po)
po.location=(100.80,0.55,1.05); po.rotation_euler=(0,0,0)
# bag fill (s5 reveal)
bl=bpy.data.lights.new('BAG_FILL','AREA'); bl.energy=0; bl.size=1.2; bl.color=(1.0,0.85,0.7); bo=bpy.data.objects.new('BAG_FILL',bl); sc.collection.objects.link(bo)
# ---- render settings
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=32; sc.cycles.adaptive_threshold=0.03; sc.cycles.use_denoising=True; sc.cycles.denoiser='OPENIMAGEDENOISE'
sc.cycles.max_bounces=6; sc.cycles.diffuse_bounces=2; sc.cycles.glossy_bounces=3; sc.cycles.transmission_bounces=8; sc.cycles.volume_bounces=0; sc.cycles.transparent_max_bounces=8
sc.cycles.volume_step_rate=3.0; sc.cycles.volume_max_steps=96; sc.cycles.caustics_reflective=False; sc.cycles.caustics_refractive=False; sc.cycles.blur_glossy=1.0
sc.render.use_persistent_data=True; sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.fps=24
sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'; sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=94
# ---- compositor: mist haze (air shots), glare on the sun, warm sunrise grade
sc.view_layers[0].use_pass_mist=True; w.mist_settings.start=25; w.mist_settings.depth=260; w.mist_settings.falloff='QUADRATIC'
sc.use_nodes=True; ct=sc.node_tree; ct.nodes.clear(); rlay=ct.nodes.new('CompositorNodeRLayers'); comp=ct.nodes.new('CompositorNodeComposite')
mm=ct.nodes.new('CompositorNodeMath'); mm.name='HAZE_AMT'; mm.operation='MULTIPLY'; mm.inputs[1].default_value=0.18
hz=ct.nodes.new('CompositorNodeMixRGB'); hz.inputs[2].default_value=(0.95,0.72,0.52,1)
ct.links.new(rlay.outputs['Mist'],mm.inputs[0]); ct.links.new(mm.outputs[0],hz.inputs[0]); ct.links.new(rlay.outputs['Image'],hz.inputs[1])
gl=ct.nodes.new('CompositorNodeGlare'); gl.glare_type='FOG_GLOW'; gl.quality='MEDIUM'; gl.threshold=1.2; gl.size=8; gl.mix=-0.6; ct.links.new(hz.outputs[0],gl.inputs[0])
cb=ct.nodes.new('CompositorNodeColorBalance'); cb.name='GRADE'; cb.correction_method='LIFT_GAMMA_GAIN'; cb.lift=(0.98,1.0,1.03); cb.gamma=(1.0,0.99,0.97); cb.gain=(1.04,1.0,0.95)
ct.links.new(gl.outputs[0],cb.inputs[1]); ct.links.new(cb.outputs[0],comp.inputs[0])
for o in bpy.data.objects:
    if o.type=='LIGHT': o.visible_camera=False

# ---- photo textures (Higgsfield): grass on dykes, mud on pond floor, weathered planks on the dock
def imgtex(n,l,path,scale,blend=0.25):
    tc=n.new('ShaderNodeTexCoord'); mp=n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(scale,scale,scale); l.new(tc.outputs['Object'],mp.inputs[0])
    t=n.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(S+'tex/'+path,check_existing=True); t.projection='BOX'; t.projection_blend=blend; l.new(mp.outputs[0],t.inputs[0]); return t
def photo(name,path,scale,tint=(1,1,1),rough=0.9,bstr=0.35):
    m=bpy.data.materials[name]; n=m.node_tree.nodes; l=m.node_tree.links; b=[x for x in n if x.type=='BSDF_PRINCIPLED'][0]
    t=imgtex(n,l,path,scale); big=noise(n,l,0.05,4,0.5); hv=ramp(n,l,big.outputs['Fac'],(0.78*tint[0],0.78*tint[1],0.78*tint[2]),(1.15*tint[0],1.1*tint[1],1.0*tint[2]),0.3,0.7)
    mu=n.new('ShaderNodeMix'); mu.data_type='RGBA'; mu.blend_type='MULTIPLY'; mu.inputs['Factor'].default_value=1.0; l.new(t.outputs['Color'],mu.inputs['A']); l.new(hv.outputs[0],mu.inputs['B'])
    return m,n,l,b,t,mu
m,n,l,b,t,mu=photo('MAT_Dyke_Earth','grass.png',0.35,(0.95,1.0,0.85))
l.new(mu.outputs['Result'],b.inputs['Base Color']); bump(n,l,t.outputs['Color'],b,0.35,0.03)
m,n,l,b,t,mu=photo('MAT_HDPE_Liner','mud.png',0.6,(0.85,0.85,0.8))
mx=[x for x in n if x.type=='MIX' and x.data_type=='RGBA' and x.inputs['A'].is_linked and x!=mu][0]; l.new(mu.outputs['Result'],mx.inputs['A'])
m,n,l,b,t,mu=photo('MAT_Walkway_Wood_Weathered','wood.png',0.9,(0.9,0.82,0.72))
l.new(mu.outputs['Result'],b.inputs['Base Color']); bump(n,l,t.outputs['Color'],b,0.3,0.004)
bpy.ops.wm.save_as_mainfile(filepath=S+'film/film.blend'); print('LOOK_SAVED')
