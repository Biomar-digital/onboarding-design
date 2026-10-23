# Look-dev: the client's Fish_Feeding salmon with a photo-matched material, in a turquoise RAS water volume.
import bpy, bmesh, sys, math, random, mathutils, os
OUT=sys.argv[sys.argv.index('--')+1]; HERE=os.path.dirname(os.path.abspath(__file__))
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
# ---- material: the client's original glTF material, untouched
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
for i in range(70): fish.append(dup_fish())
# placements: hero fish near camera, the rest receding into the haze (camera looks up at ~12 deg)
spots=[(0.55,0.75,0.55,1.1),(-0.55,0.05,0.45,1.15),(1.15,0.45,-0.2,1.1),(-0.2,1.5,1.1,1.0),(0.9,2.2,-0.6,1.0),(-1.6,2.0,1.6,0.95)]
for i,(r,a) in enumerate(fish):
    if i<len(spots): x,y,z,s=spots[i]
    else: x,y,z,s=random.uniform(-6,6),random.uniform(2.5,16),random.uniform(-3.0,4.4),random.uniform(0.85,1.15)
    r.location=(x,y,z); r.scale=(0.7/L*s,)*3
    # most of the school circles one way, ~1/4 heads the other way or toward/away from camera
    yaw=90+random.uniform(-35,35) if random.random()<0.75 else random.choice([-90,0,180])+random.uniform(-30,30)
    if i==1: yaw=100          # big foreground fish crossing left-front
    r.rotation_euler=(math.radians(random.uniform(-14,14)),math.radians(random.uniform(-25,25)),math.radians(yaw))
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
sun=bpy.data.lights.new('sun','SUN'); sun.energy=34; sun.color=(0.92,0.98,1.0); sun.angle=math.radians(2)
so=bpy.data.objects.new('sun',sun); sc.collection.objects.link(so); so.rotation_euler=(math.radians(-30),math.radians(25),math.radians(-20))
# water surface (rippled, refractive) above the fish
surf=mk('Surface',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=200)); surf.location=(0,30,5.2)
sm=bpy.data.materials.new('surf'); sm.use_nodes=True; sb=sm.node_tree.nodes['Principled BSDF']; sb.inputs['Transmission Weight'].default_value=1; sb.inputs['Roughness'].default_value=0.05; sb.inputs['IOR'].default_value=1.33
sn=sm.node_tree; wv=sn.nodes.new('ShaderNodeTexNoise'); wv.inputs['Scale'].default_value=3.5; wv.inputs['Detail'].default_value=8; wv.inputs['Distortion'].default_value=1.5
bmp=sn.nodes.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value=1.0; sn.links.new(wv.outputs['Fac'],bmp.inputs['Height']); sn.links.new(bmp.outputs['Normal'],sb.inputs['Normal'])
surf.data.materials.append(sm); surf.visible_shadow=False
# gobo: invisible to the camera, only shadows -> light shafts through the water volume
gobo=mk('Gobo',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=200)); gobo.location=(0,30,4.9)
gm=bpy.data.materials.new('gobo'); gm.use_nodes=True; gn=gm.node_tree; gb=gn.nodes['Principled BSDF']
cv=gn.nodes.new('ShaderNodeTexVoronoi'); cv.feature='DISTANCE_TO_EDGE'; cv.inputs['Scale'].default_value=1.4
gco=gn.nodes.new('ShaderNodeTexCoord'); wrp=gn.nodes.new('ShaderNodeTexNoise'); wrp.inputs['Scale'].default_value=0.6
wad=gn.nodes.new('ShaderNodeVectorMath'); wad.operation='ADD'; gn.links.new(gco.outputs['Object'],wad.inputs[0]); gn.links.new(wrp.outputs['Color'],wad.inputs[1])
gn.links.new(gco.outputs['Object'],wrp.inputs['Vector']); gn.links.new(wad.outputs[0],cv.inputs['Vector'])
gr=gn.nodes.new('ShaderNodeValToRGB'); gr.color_ramp.elements[0].position=0.05; gr.color_ramp.elements[0].color=(1,1,1,1)
gr.color_ramp.elements[1].position=0.16; gr.color_ramp.elements[1].color=(0.12,0.12,0.12,1)   # lines let light through, cells only a little
gn.links.new(cv.outputs['Distance'],gr.inputs[0]); inv=gn.nodes.new('ShaderNodeInvert'); gn.links.new(gr.outputs['Color'],inv.inputs['Color'])
gn.links.new(inv.outputs['Color'],gb.inputs['Alpha']); gb.inputs['Base Color'].default_value=(0,0,0,1)
gobo.data.materials.append(gm)
for v in ('visible_camera','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter'): setattr(gobo,v,False)
# bright sky above the surface, seen through the ripples (sun glow up-left)
sky=mk('Sky',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=200)); sky.location=(0,30,9)
km=bpy.data.materials.new('sky'); km.use_nodes=True; kn=km.node_tree; kn.nodes.remove(kn.nodes['Principled BSDF'])
em=kn.nodes.new('ShaderNodeEmission'); kgr=kn.nodes.new('ShaderNodeTexGradient'); kgr.gradient_type='SPHERICAL'
kmap=kn.nodes.new('ShaderNodeMapping'); kmap.inputs['Location'].default_value=(0.03,-0.05,0); kmap.inputs['Scale'].default_value=(0.018,0.018,1)
kco=kn.nodes.new('ShaderNodeTexCoord'); kn.links.new(kco.outputs['Object'],kmap.inputs['Vector']); kn.links.new(kmap.outputs[0],kgr.inputs['Vector'])
kr=kn.nodes.new('ShaderNodeValToRGB'); kr.color_ramp.elements[0].color=(0.35,0.55,0.6,1); kr.color_ramp.elements[1].color=(1.9,2.1,2.1,1); kr.color_ramp.elements[1].position=0.97
kn.links.new(kgr.outputs['Fac'],kr.inputs[0]); kn.links.new(kr.outputs['Color'],em.inputs['Color']); em.inputs['Strength'].default_value=1.6
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
tr=dn.nodes.new('ShaderNodeBsdfTransparent'); dsc=dn.nodes.new('ShaderNodeBsdfTranslucent'); dsc.inputs['Color'].default_value=(0.9,0.97,0.95,1)
dmx=dn.nodes.new('ShaderNodeMixShader'); dmx.inputs['Fac'].default_value=0.45; dn.links.new(tr.outputs[0],dmx.inputs[1]); dn.links.new(dsc.outputs[0],dmx.inputs[2])
dn.links.new(dmx.outputs[0],dn.nodes['Material Output'].inputs['Surface'])
random.seed(3)
flakes=[]
for k in range(16):
    f=mk(f'Flake{k}',flake); f.data.materials.append(dm); f.location=(0,-50,0); f.visible_shadow=False; flakes.append(f)
def scatter(n,base,spread,yr,zr):
    for i in range(n):
        d=random.choice(flakes).copy(); sc.collection.objects.link(d)
        d.location=(random.uniform(-4,4),random.uniform(*yr),random.uniform(*zr))
        sz=base*math.exp(random.gauss(0,spread)); d.scale=(sz*random.uniform(0.5,1.5),sz*random.uniform(0.5,1.5),sz)
        d.rotation_euler=(random.uniform(0,6.28),random.uniform(0,6.28),random.uniform(0,6.28))
scatter(4200,0.0012,0.45,(0.1,8),(-2,4.5))     # fine dust
scatter(140,0.006,0.35,(0.2,5),(-1.5,4))       # fluffy flocs
# bubble plumes from the oxygen diffusers: real spheres, glassy rim
bm_=bpy.data.materials.new('bubble'); bm_.use_nodes=True; bb=bm_.node_tree.nodes['Principled BSDF']
bb.inputs['Transmission Weight'].default_value=1; bb.inputs['IOR'].default_value=0.75; bb.inputs['Roughness'].default_value=0.0
bub=mk('Bubble',lambda bm: bmesh.ops.create_uvsphere(bm,u_segments=16,v_segments=8,radius=1.0)); bub.data.materials.append(bm_); bub.location=(0,-50,0)
for p in bub.data.polygons: p.use_smooth=True
for (px,py) in [(-2.6,4.5),(2.2,6.5),(-0.6,9.0)]:
    for i in range(160):
        d=bub.copy(); sc.collection.objects.link(d); h=random.uniform(-3,5)
        d.location=(px+random.gauss(0,0.12+0.03*(h+3)),py+random.gauss(0,0.12+0.03*(h+3)),h)
        r_=random.uniform(0.0015,0.006); d.scale=(r_,r_,r_*0.8); d.visible_shadow=False
# tank bottom falling to dark: a dark floor far below so depth reads
floor=mk('Floor',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=200)); floor.location=(0,30,-6)
fm=bpy.data.materials.new('floor'); fm.use_nodes=True; fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.02,0.04,0.045,1); floor.data.materials.append(fm)
# camera: below the hero fish, looking up toward the light (like the reference photo)
cam=bpy.data.cameras.new('cam'); cam.lens=20; co=bpy.data.objects.new('cam',cam); sc.collection.objects.link(co); sc.camera=co
co.location=(0.45,-1.0,-0.05); co.rotation_euler=(math.radians(109),0,math.radians(10))
# real depth of field: focus on the hero salmon, near flakes go soft
cam.dof.use_dof=True; cam.dof.aperture_fstop=2.0; cam.dof.focus_distance=1.85
ANIM='--anim' in sys.argv
F=int(sys.argv[sys.argv.index('--anim')+1]) if ANIM else 1
sc.frame_start=1; sc.frame_end=F; sc.render.fps=24
def lin(ob,attr,v0,v1):
    setattr(ob,attr,v0); ob.keyframe_insert(attr,frame=1); setattr(ob,attr,v1); ob.keyframe_insert(attr,frame=F)
    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation='LINEAR'
if ANIM:
    # ---- schooling (boids): a vigorous school following a meandering lead along the tank's circular flow
    import numpy as np
    random.seed(11)
    CY=34.0; R0=30.0; VL=1.05; DT=1/24; X0=-6.5
    NS=58                                                      # fish in the school; the rest swim alone
    def lead(t):
        th=-math.pi/2+(X0+VL*t)/R0; rr=R0+0.3*math.sin(0.3*t)
        p=np.array([rr*math.cos(th),CY+rr*math.sin(th),0.9+0.25*math.sin(0.4*t+1.0)])
        e=0.02; th2=-math.pi/2+(X0+VL*(t+e))/R0; rr2=R0+0.3*math.sin(0.3*(t+e))
        p2=np.array([rr2*math.cos(th2),CY+rr2*math.sin(th2),0.9+0.25*math.sin(0.4*(t+e)+1.0)])
        return p,(p2-p)/e
    sys.path.insert(0,HERE); from school import simulate
    trackP,trackV=simulate(lead,F,NS)
    def orient(v,prev_yaw,prev_bank):
        yaw=math.atan2(v[0],-v[1]); h=math.hypot(v[0],v[1]); pitch=max(-0.21,min(0.21,-math.atan2(v[2],h)))
        dyaw=(yaw-prev_yaw+math.pi)%(2*math.pi)-math.pi if prev_yaw is not None else 0.0
        bank=0.85*(prev_bank or 0)+0.15*max(-0.35,min(0.35,-dyaw*24*0.3))  # gentle lean into turns
        return pitch,bank,(prev_yaw+dyaw) if prev_yaw is not None else yaw
    for i,(r,a) in enumerate(fish):
        if i<NS:
            yw=None; bk=None; sc_=r.scale.copy()
            for f in range(F):
                pitch,bk,yw=orient(trackV[f,i],yw,bk)
                r.location=trackP[f,i]; r.rotation_euler=(pitch,bk,yw)
                r.keyframe_insert('location',frame=f+1); r.keyframe_insert('rotation_euler',frame=f+1)
            v=float(np.linalg.norm(trackV[:,i],axis=1).mean())
        else:   # loners: slow curved cruise at their own depth
            x0,y0,z0=r.location; R=max(1.5,math.hypot(x0,y0-CY)); th0=math.atan2(y0-CY,x0)
            sense=1 if random.random()<0.7 else -1; v=random.uniform(0.4,0.7)
            yw=None; bk=None
            for f in range(F):
                t=f*DT; th=th0+sense*v*t/R; z=z0+0.2*math.sin(0.8*t+i)
                p=mathutils.Vector((R*math.cos(th),CY+R*math.sin(th),z))
                vv=np.array([-math.sin(th)*sense*v,math.cos(th)*sense*v,0.16*math.cos(0.8*t+i)])
                pitch,bk,yw=orient(vv,yw,bk); r.location=p; r.rotation_euler=(pitch,bk,yw)
                r.keyframe_insert('location',frame=f+1); r.keyframe_insert('rotation_euler',frame=f+1)
        # vigorous tail beat: the swim cycle runs faster the faster the fish goes
        for tr in a.animation_data.nla_tracks:
            for st in tr.strips: st.scale=max(0.3,min(1.0,0.38/v)); st.repeat=14
    drift=bpy.data.objects.new('Drift',None); sc.collection.objects.link(drift)
    rise=bpy.data.objects.new('Rise',None); sc.collection.objects.link(rise)
    for o in list(sc.objects):
        if o.name.startswith('Flake') : o.parent=drift
        if o.name.startswith('Bubble'): o.parent=rise
    lin(drift,'location',(0,0,0),(0.04*F/24,-0.02*F/24,0.015*F/24)); lin(rise,'location',(0,0,0),(0,0,0.35*F/24))
    sc.render.image_settings.file_format='PNG'
else:
    sc.frame_set(40)
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=64; sc.cycles.use_denoising=True
sc.cycles.volume_step_rate=4; sc.cycles.max_bounces=6
sc.render.resolution_x=960; sc.render.resolution_y=540; sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - High Contrast'
sc.use_nodes=True; ct=sc.node_tree; rl=ct.nodes['Render Layers']; comp=ct.nodes['Composite']
gl=ct.nodes.new('CompositorNodeGlare'); gl.glare_type='FOG_GLOW'; gl.quality='HIGH'; gl.threshold=1.1; gl.size=8
ld=ct.nodes.new('CompositorNodeLensdist'); ld.inputs['Dispersion'].default_value=0.012
el=ct.nodes.new('CompositorNodeEllipseMask'); el.width=1.15; el.height=1.0
bl=ct.nodes.new('CompositorNodeBlur'); bl.size_x=220; bl.size_y=220; bl.use_relative=False
mx=ct.nodes.new('CompositorNodeMixRGB'); mx.blend_type='MULTIPLY'
vg=ct.nodes.new('CompositorNodeMapRange'); vg.inputs[3].default_value=0.62; vg.inputs[4].default_value=1.0
ct.links.new(rl.outputs['Image'],gl.inputs['Image']); ct.links.new(gl.outputs['Image'],ld.inputs['Image'])
ct.links.new(el.outputs['Mask'],bl.inputs['Image']); ct.links.new(bl.outputs['Image'],vg.inputs['Value'])
ct.links.new(ld.outputs['Image'],mx.inputs[1]); ct.links.new(vg.outputs['Value'],mx.inputs[2]); ct.links.new(mx.outputs['Image'],comp.inputs['Image'])
if ANIM:   # preview-only settings, applied last so nothing overrides them
    sc.render.resolution_x=640; sc.render.resolution_y=360; sc.cycles.samples=24
    dust=[o for o in sc.objects if o.name.startswith('Flake') and '.' in o.name]
    for o in dust[1500:]: o.hide_render=True
    sc.cycles.volume_step_rate=10; sc.cycles.max_bounces=3; sc.cycles.transparent_max_bounces=4; sc.cycles.volume_bounces=0
    sc.render.image_settings.file_format='PNG'
sc.render.filepath=OUT; bpy.ops.render.render(write_still=not ANIM, animation=ANIM)
bpy.ops.wm.save_as_mainfile(filepath=(OUT.rstrip('/')+'.blend') if ANIM else OUT.replace('.png','.blend'))
print('DONE')
