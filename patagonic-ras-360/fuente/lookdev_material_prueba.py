# Look-dev: the client's Fish_Feeding salmon with a photo-matched material, in a turquoise RAS water volume.
import bpy, bmesh, sys, math, random, mathutils, os
OUT=sys.argv[sys.argv.index('--')+1]; HERE=os.path.dirname(os.path.abspath(OUT))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
bpy.ops.import_scene.gltf(filepath=os.path.join(HERE,'fish_feeding.glb'))
arm=[o for o in sc.objects if o.type=='ARMATURE'][0]
body=max([o for o in sc.objects if o.type=='MESH'],key=lambda o:len(o.data.vertices))
act=bpy.data.actions[0]
for o in sc.objects:
    if o.name.startswith('Icosphere'): o.hide_render=True; o.hide_viewport=True
# ---- root of the imported hierarchy, scaled to a 70 cm salmon
roots=[o for o in sc.objects if o.parent is None]
root=bpy.data.objects.new('FishRoot',None); sc.collection.objects.link(root)
for o in roots: o.parent=root
bpy.context.view_layer.update()
bb=[body.matrix_world@mathutils.Vector(c) for c in body.bound_box]
L=max(max(v[i] for v in bb)-min(v[i] for v in bb) for i in range(3))
root.scale=(0.7/L,)*3; bpy.context.view_layer.update()
# local axis of the body mesh that points up in the world
mw=body.matrix_world.to_3x3()
up_ax=max(range(3),key=lambda i:abs(mw.col[i].z)); up_sign=1 if mw.col[up_ax].z>0 else -1
vs=[v.co[up_ax]*up_sign for v in body.data.vertices]; lo,hi=min(vs),max(vs)
print('UP AXIS',up_ax,up_sign,lo,hi)
# ---- material: keep the scale texture, add photo colour gradient, black spots, wet sheen
mat=body.active_material; nt=mat.node_tree; N=nt.nodes; Lk=nt.links
bsdf=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]
tex=[n for n in N if n.type=='TEX_IMAGE'][0]
tc=N.new('ShaderNodeTexCoord'); sep=N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['Object'],sep.inputs[0])
h=N.new('ShaderNodeMapRange'); Lk.new(sep.outputs[up_ax],h.inputs['Value'])
h.inputs['From Min'].default_value=lo if up_sign>0 else -hi; h.inputs['From Max'].default_value=hi if up_sign>0 else -lo
if up_sign<0:
    neg=N.new('ShaderNodeMath'); neg.operation='MULTIPLY'; neg.inputs[1].default_value=-1
    Lk.new(sep.outputs[up_ax],neg.inputs[0]); Lk.new(neg.outputs[0],h.inputs['Value'])
ramp=N.new('ShaderNodeValToRGB'); Lk.new(h.outputs[0],ramp.inputs[0]); cr=ramp.color_ramp
cr.elements[0].position=0.0; cr.elements[0].color=(0.86,0.88,0.88,1)            # belly
cr.elements[1].position=1.0; cr.elements[1].color=(0.012,0.022,0.03,1)           # dark slate back
e=cr.elements.new(0.40); e.color=(0.42,0.47,0.5,1)                                # silver flank
e=cr.elements.new(0.62); e.color=(0.07,0.1,0.12,1)                               # blue-grey upper flank
# black spots on the upper half
vor=N.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value=650.0; Lk.new(tc.outputs['Object'],vor.inputs['Vector'])
sp=N.new('ShaderNodeMapRange'); Lk.new(vor.outputs['Distance'],sp.inputs['Value']); sp.inputs['From Min'].default_value=0.10; sp.inputs['From Max'].default_value=0.16
upper=N.new('ShaderNodeMapRange'); Lk.new(h.outputs[0],upper.inputs['Value']); upper.inputs['From Min'].default_value=0.42; upper.inputs['From Max'].default_value=0.6
inv=N.new('ShaderNodeMath'); inv.operation='SUBTRACT'; inv.inputs[0].default_value=1; Lk.new(sp.outputs[0],inv.inputs[1])
spot=N.new('ShaderNodeMath'); spot.operation='MULTIPLY'; Lk.new(inv.outputs[0],spot.inputs[0]); Lk.new(upper.outputs[0],spot.inputs[1])
mixs=N.new('ShaderNodeMix'); mixs.data_type='RGBA'; Lk.new(spot.outputs[0],mixs.inputs['Factor'])
Lk.new(ramp.outputs[0],mixs.inputs[6]); mixs.inputs[7].default_value=(0.01,0.012,0.015,1)
# scale detail from the original texture (luminance multiplied in)
bw=N.new('ShaderNodeRGBToBW'); Lk.new(tex.outputs['Color'],bw.inputs[0])
det=N.new('ShaderNodeMapRange'); Lk.new(bw.outputs[0],det.inputs['Value']); det.inputs['From Min'].default_value=0.15; det.inputs['From Max'].default_value=0.75; det.inputs['To Min'].default_value=0.7; det.inputs['To Max'].default_value=1.15
mul=N.new('ShaderNodeMix'); mul.data_type='RGBA'; mul.blend_type='MULTIPLY'; mul.inputs['Factor'].default_value=1.0
Lk.new(mixs.outputs[2],mul.inputs[6]); Lk.new(det.outputs[0],mul.inputs[7])
Lk.new(mul.outputs[2],bsdf.inputs['Base Color'])
# silver flanks are metallic, back less so; wet coat everywhere
met=N.new('ShaderNodeMapRange'); Lk.new(h.outputs[0],met.inputs['Value']); met.inputs['From Min'].default_value=0.2; met.inputs['From Max'].default_value=0.8; met.inputs['To Min'].default_value=0.55; met.inputs['To Max'].default_value=0.05
Lk.new(met.outputs[0],bsdf.inputs['Metallic'])
bsdf.inputs['Roughness'].default_value=0.42
bsdf.inputs['Coat Weight'].default_value=0.25; bsdf.inputs['Coat Roughness'].default_value=0.2
# ---- school: duplicate the whole fish with offset animation phases
def dup_fish():
    objs=[root]+[o for o in root.children_recursive if not o.name.startswith('Icosphere')]   # skip the importer's bone-display sphere
    m={}
    for o in objs:
        c=o.copy();
        if o.type=='ARMATURE': c.animation_data_clear()
        sc.collection.objects.link(c); m[o]=c
    for o,c in m.items():
        if o.parent in m: c.parent=m[o.parent]
        for md in c.modifiers:
            if md.type=='ARMATURE' and md.object in m: md.object=m[md.object]
    return m[root],[c for o,c in m.items() if o.type=='ARMATURE'][0]
random.seed(7)
fr=act.frame_range
def set_phase(a,ph):
    a.animation_data_create(); tr=a.animation_data.nla_tracks.new(); st=tr.strips.new('swim',int(fr[0]),act)
    st.repeat=4; st.frame_start=fr[0]-ph
arm.animation_data.action=None; set_phase(arm,0)
fish=[(root,arm)]
for i in range(40): fish.append(dup_fish())
# placements: hero fish near camera, the rest receding into the haze (camera looks up at ~12 deg)
spots=[(0.55,0.55,0.15,1.1),(-0.2,1.3,0.05,1.0),(0.9,2.0,-0.9,1.0),(-1.6,1.8,1.1,0.95)]
for i,(r,a) in enumerate(fish):
    if i<len(spots): x,y,z,s=spots[i]
    else: x,y,z,s=random.uniform(-5,5),random.uniform(2.5,12),random.uniform(-2.5,3.8),random.uniform(0.85,1.15)
    r.location=(x,y,z); r.scale=(0.7/L*s,)*3
    r.rotation_euler=(math.radians(random.uniform(-12,12)),math.radians(random.uniform(-22,22)),math.radians(90+random.uniform(-40,40)))
    if i: set_phase(a,random.randint(0,190))
def mk(name,build):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); build(bm); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); sc.collection.objects.link(ob); return ob
# ---- water: turquoise volume, sun through the surface, particles
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True; wn=w.node_tree
wn.nodes['Background'].inputs[0].default_value=(0.16,0.3,0.31,1); wn.nodes['Background'].inputs[1].default_value=0.6
# water volume as a bounded block (a world volume is infinite and swallows the sun)
box=mk('WaterBox',lambda bm: bmesh.ops.create_cube(bm,size=1.0)); box.location=(0,30,-4.5); box.scale=(200,200,19.2)
vm=bpy.data.materials.new('water'); vm.use_nodes=True; vn=vm.node_tree; vn.nodes.remove(vn.nodes['Principled BSDF'])
vol=vn.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Color'].default_value=(0.24,0.46,0.45,1); vol.inputs['Density'].default_value=0.085
vol.inputs['Anisotropy'].default_value=0.75; vol.inputs['Absorption Color'].default_value=(0.45,0.72,0.7,1)
vn.links.new(vol.outputs[0],vn.nodes['Material Output'].inputs['Volume']); box.data.materials.append(vm)
sun=bpy.data.lights.new('sun','SUN'); sun.energy=22; sun.color=(0.92,0.98,1.0); sun.angle=math.radians(2)
so=bpy.data.objects.new('sun',sun); sc.collection.objects.link(so); so.rotation_euler=(math.radians(-30),math.radians(25),math.radians(-20))
# water surface (rippled, refractive) above the fish
surf=mk('Surface',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=200)); surf.location=(0,30,5.2)
sm=bpy.data.materials.new('surf'); sm.use_nodes=True; sb=sm.node_tree.nodes['Principled BSDF']; sb.inputs['Transmission Weight'].default_value=1; sb.inputs['Roughness'].default_value=0.05; sb.inputs['IOR'].default_value=1.33
sn=sm.node_tree; wv=sn.nodes.new('ShaderNodeTexNoise'); wv.inputs['Scale'].default_value=1.6; wv.inputs['Detail'].default_value=4
bmp=sn.nodes.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value=0.6; sn.links.new(wv.outputs['Fac'],bmp.inputs['Height']); sn.links.new(bmp.outputs['Normal'],sb.inputs['Normal'])
surf.data.materials.append(sm); surf.visible_shadow=False
# gobo: invisible to the camera, only shadows -> light shafts through the water volume
gobo=mk('Gobo',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=200)); gobo.location=(0,30,4.9)
gm=bpy.data.materials.new('gobo'); gm.use_nodes=True; gn=gm.node_tree; gb=gn.nodes['Principled BSDF']
nz=gn.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=2.2; nz.inputs['Detail'].default_value=3
gco=gn.nodes.new('ShaderNodeTexCoord'); gn.links.new(gco.outputs['Object'],nz.inputs['Vector'])
gr=gn.nodes.new('ShaderNodeValToRGB'); gr.color_ramp.elements[0].position=0.47; gr.color_ramp.elements[1].position=0.53
gn.links.new(nz.outputs['Fac'],gr.inputs[0]); gn.links.new(gr.outputs['Color'],gb.inputs['Alpha']); gb.inputs['Base Color'].default_value=(0,0,0,1)
gobo.data.materials.append(gm)
for v in ('visible_camera','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter'): setattr(gobo,v,False)
# bright sky above the surface, seen through the ripples (sun glow up-left)
sky=mk('Sky',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=200)); sky.location=(0,30,9)
km=bpy.data.materials.new('sky'); km.use_nodes=True; kn=km.node_tree; kn.nodes.remove(kn.nodes['Principled BSDF'])
em=kn.nodes.new('ShaderNodeEmission'); kgr=kn.nodes.new('ShaderNodeTexGradient'); kgr.gradient_type='SPHERICAL'
kmap=kn.nodes.new('ShaderNodeMapping'); kmap.inputs['Location'].default_value=(0.10,-0.1,0); kmap.inputs['Scale'].default_value=(0.02,0.02,1)
kco=kn.nodes.new('ShaderNodeTexCoord'); kn.links.new(kco.outputs['Object'],kmap.inputs['Vector']); kn.links.new(kmap.outputs[0],kgr.inputs['Vector'])
kr=kn.nodes.new('ShaderNodeValToRGB'); kr.color_ramp.elements[0].color=(0.35,0.55,0.6,1); kr.color_ramp.elements[1].color=(4.0,4.4,4.4,1); kr.color_ramp.elements[1].position=0.85
kn.links.new(kgr.outputs['Fac'],kr.inputs[0]); kn.links.new(kr.outputs['Color'],em.inputs['Color']); em.inputs['Strength'].default_value=3.0
kn.links.new(em.outputs[0],kn.nodes['Material Output'].inputs['Surface']); sky.data.materials.append(km); sky.visible_shadow=False
fill=bpy.data.lights.new('fill','AREA'); fill.energy=70; fill.size=6; fill.color=(0.6,0.85,0.85)
fo=bpy.data.objects.new('fill',fill); sc.collection.objects.link(fo); fo.location=(0,-2,-3); fo.rotation_euler=(math.radians(-120),0,0)
# suspended particles
def flake(bm):
    # an irregular, flattened blob: icosphere with each vertex pushed in/out at random, then squashed
    bmesh.ops.create_icosphere(bm,subdivisions=1,radius=1.0)
    for v in bm.verts: v.co*=random.uniform(0.45,1.25)
    for v in bm.verts: v.co.z*=0.35
dm=bpy.data.materials.new('snow'); dm.use_nodes=True; dn=dm.node_tree; dn.nodes.remove(dn.nodes['Principled BSDF'])
tr=dn.nodes.new('ShaderNodeBsdfTransparent'); dsc=dn.nodes.new('ShaderNodeBsdfDiffuse'); dsc.inputs['Color'].default_value=(0.85,0.95,0.93,1)
de=dn.nodes.new('ShaderNodeEmission'); de.inputs['Color'].default_value=(0.75,0.9,0.9,1); de.inputs['Strength'].default_value=0.25
ad=dn.nodes.new('ShaderNodeAddShader'); dn.links.new(dsc.outputs[0],ad.inputs[0]); dn.links.new(de.outputs[0],ad.inputs[1])
dmx=dn.nodes.new('ShaderNodeMixShader'); dmx.inputs['Fac'].default_value=0.3; dn.links.new(tr.outputs[0],dmx.inputs[1]); dn.links.new(ad.outputs[0],dmx.inputs[2])
dn.links.new(dmx.outputs[0],dn.nodes['Material Output'].inputs['Surface'])
random.seed(3)
flakes=[]
for k in range(12):
    f=mk(f'Flake{k}',flake); f.data.materials.append(dm); f.location=(0,-50,0); f.visible_shadow=False; flakes.append(f)
for i in range(2600):
    src=random.choice(flakes); d=src.copy(); sc.collection.objects.link(d)
    d.location=(random.uniform(-3.5,3.5),random.uniform(0.15,7),random.uniform(-1.8,3.8))
    sz=0.0035*math.exp(random.gauss(0,0.6))            # mostly tiny, a few larger
    d.scale=(sz*random.uniform(0.6,1.4),sz*random.uniform(0.6,1.4),sz)
    d.rotation_euler=(random.uniform(0,6.28),random.uniform(0,6.28),random.uniform(0,6.28))
# camera: below the hero fish, looking up toward the light (like the reference photo)
cam=bpy.data.cameras.new('cam'); cam.lens=20; co=bpy.data.objects.new('cam',cam); sc.collection.objects.link(co); sc.camera=co
co.location=(0.5,-0.95,0.12); co.rotation_euler=(math.radians(96),0,math.radians(8))
# real depth of field: focus on the hero salmon, near flakes go soft
cam.dof.use_dof=True; cam.dof.aperture_fstop=2.0; cam.dof.focus_distance=1.55
sc.frame_set(40)
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=64; sc.cycles.use_denoising=True
sc.cycles.volume_step_rate=4; sc.cycles.max_bounces=6
sc.render.resolution_x=960; sc.render.resolution_y=540; sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - High Contrast'
sc.render.filepath=OUT; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT.replace('.png','.blend'))
print('DONE')
