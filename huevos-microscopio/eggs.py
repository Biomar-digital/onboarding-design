# Fish eggs under a brightfield microscope: chorion with double edge, granular yolk, dark oil globule (a lens:
# black rim, bright centre), and a curled translucent embryo with somites, head and eye. Cycles, back-lit.
# blender -b --factory-startup -P eggs.py -- OUT.png [samples] [width]
import bpy, bmesh, math, random, sys, mathutils
args=sys.argv[sys.argv.index('--')+1:]; OUT=args[0]; SPP=int(args[1]) if len(args)>1 else 96; RW=int(args[2]) if len(args)>2 else 1600
bpy.ops.wm.read_factory_settings(use_empty=True); sc=bpy.context.scene; random.seed(4)
def sphere(name,r,loc,seg=48):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); bmesh.ops.create_uvsphere(bm,u_segments=seg,v_segments=seg//2,radius=r); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    o=bpy.data.objects.new(name,me); sc.collection.objects.link(o); o.location=loc; return o
def mat(name):
    m=bpy.data.materials.new(name); m.use_nodes=True; return m,m.node_tree.nodes,m.node_tree.links
# ---- materials
chor,N,Lk=mat('chorion'); b=N['Principled BSDF']; b.inputs['Base Color'].default_value=(0.9,0.97,0.94,1)
b.inputs['Transmission Weight'].default_value=1; b.inputs['IOR'].default_value=1.04; b.inputs['Roughness'].default_value=0.03
peri,N,Lk=mat('perivitelline'); b=N['Principled BSDF']; b.inputs['Transmission Weight'].default_value=1; b.inputs['IOR'].default_value=1.005; b.inputs['Roughness'].default_value=0.05
b.inputs['Base Color'].default_value=(0.97,0.96,0.97,1)
yolk,N,Lk=mat('yolk'); b=N['Principled BSDF']; b.inputs['Transmission Weight'].default_value=1; b.inputs['IOR'].default_value=1.02; b.inputs['Roughness'].default_value=0.15
b.inputs['Base Color'].default_value=(0.96,0.93,0.92,1)
v=N.new('ShaderNodeVolumePrincipled'); v.inputs['Color'].default_value=(0.82,0.78,0.78,1); v.inputs['Absorption Color'].default_value=(0.75,0.7,0.7,1)
nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=55; nz.inputs['Detail'].default_value=1.5
gr=N.new('ShaderNodeMapRange'); Lk.new(nz.outputs['Fac'],gr.inputs[0]); gr.inputs[1].default_value=0.55; gr.inputs[2].default_value=0.7; gr.inputs[3].default_value=0.6; gr.inputs[4].default_value=7.0
gr.inputs[4].default_value=1.2; Lk.new(gr.outputs[0],v.inputs['Density']); Lk.new(v.outputs[0],N['Material Output'].inputs['Volume'])     # granular yolk
vo=N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value=140; vo.inputs['Randomness'].default_value=1.0
sk=N.new('ShaderNodeMapRange'); Lk.new(vo.outputs['Distance'],sk.inputs[0]); sk.inputs[1].default_value=0.06; sk.inputs[2].default_value=0.16; sk.inputs[3].default_value=0.8; sk.inputs[4].default_value=0.0
dk=N.new('ShaderNodeBsdfDiffuse'); dk.inputs['Color'].default_value=(0.15,0.12,0.12,1); mx=N.new('ShaderNodeMixShader')
Lk.new(sk.outputs[0],mx.inputs[0]); Lk.new(b.outputs[0],mx.inputs[1]); Lk.new(dk.outputs[0],mx.inputs[2]); Lk.new(mx.outputs[0],N['Material Output'].inputs['Surface'])     # stipple
oil,N,Lk=mat('oil'); b=N['Principled BSDF']; b.inputs['Transmission Weight'].default_value=1; b.inputs['IOR'].default_value=1.13; b.inputs['Roughness'].default_value=0.0
b.inputs['Base Color'].default_value=(0.95,0.95,0.9,1)
ov=N.new('ShaderNodeVolumeAbsorption'); ov.inputs['Color'].default_value=(0.55,0.5,0.4,1); ov.inputs['Density'].default_value=1.5; Lk.new(ov.outputs[0],N['Material Output'].inputs['Volume'])
emb,N,Lk=mat('embryo'); b=N['Principled BSDF']; b.inputs['Transmission Weight'].default_value=1.0; b.inputs['IOR'].default_value=1.035; b.inputs['Roughness'].default_value=0.2
b.inputs['Base Color'].default_value=(0.88,0.86,0.86,1)
tc=N.new('ShaderNodeTexCoord'); sep=N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['UV'],sep.inputs[0])
wv=N.new('ShaderNodeMath'); wv.operation='MULTIPLY'; Lk.new(sep.outputs['X'],wv.inputs[0]); wv.inputs[1].default_value=2*math.pi*30   # somites along the body
sn=N.new('ShaderNodeMath'); sn.operation='SINE'; Lk.new(wv.outputs[0],sn.inputs[0])
bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=1.0; Lk.new(sn.outputs[0],bp.inputs['Height']); Lk.new(bp.outputs['Normal'],b.inputs['Normal'])
ev=N.new('ShaderNodeVolumeAbsorption'); ev.inputs['Color'].default_value=(0.7,0.66,0.66,1); ev.inputs['Density'].default_value=0.9; Lk.new(ev.outputs[0],N['Material Output'].inputs['Volume'])
eye,N,Lk=mat('eye'); N.remove(N['Principled BSDF']); a=N.new('ShaderNodeBsdfDiffuse'); a.inputs['Color'].default_value=(0.25,0.22,0.22,1); Lk.new(a.outputs[0],N['Material Output'].inputs['Surface'])
# ---- one egg
def egg(c,rad):
    o=sphere('chorion',rad,c,64); o.data.materials.append(chor)
    sphere('peri',rad*0.965,c,64).data.materials.append(peri)
    # orientation of this egg's embryo
    R=mathutils.Euler((random.choice([random.uniform(-0.4,0.4),random.uniform(1.2,1.57)]),random.uniform(-0.4,0.4),random.uniform(0,6.28))).to_matrix()   # some seen flat, some edge-on
    yc=mathutils.Vector(c)+R@mathutils.Vector((0,0,-0.08*rad)); y=sphere('yolk',rad*0.8,yc,64); y.data.materials.append(yolk)
    # oil globule floats at the top of the yolk
    oc=yc+R@mathutils.Vector((random.uniform(-0.3,0.3)*rad,random.uniform(-0.3,0.3)*rad,0.45*rad)); sphere('oil',rad*random.uniform(0.2,0.24),oc,40).data.materials.append(oil)
    # embryo: arc around the yolk, head thick, tail thin
    cu=bpy.data.curves.new('emb','CURVE'); cu.dimensions='3D'; cu.bevel_depth=0.11*rad; cu.bevel_resolution=6
    sp=cu.splines.new('POLY'); n=40; span=random.uniform(2.2,3.6); a0=random.uniform(0,6.28); rr=rad*0.86
    sp.points.add(n-1)
    for i in range(n):
        u=i/(n-1); ang=a0+span*u; p=yc+R@mathutils.Vector((rr*math.cos(ang),rr*math.sin(ang),0.0))
        sp.points[i].co=(p.x,p.y,p.z,1); sp.points[i].radius=1.25-0.85*u**1.5
    eo=bpy.data.objects.new('embryo',cu); sc.collection.objects.link(eo); cu.materials.append(emb)
    hp=yc+R@mathutils.Vector((rr*1.02*math.cos(a0),rr*1.02*math.sin(a0),0))
    h=sphere('head',0.16*rad,hp,32); h.scale=(1.2,1.0,0.8); h.data.materials.append(emb)
    side=R@mathutils.Vector((math.cos(a0+0.25),math.sin(a0+0.25),0))
    sphere('eye',0.03*rad,hp+side*0.08*rad+R@mathutils.Vector((0,0,0.07*rad)),24).data.materials.append(eye)
# hexagonal-ish packing filling the frame, slight size variation and jitter
rad=1.0; k=0
for row in range(-3,4):
    for col in range(-4,5):
        x=col*2.3*rad+(1.15*rad if row%2 else 0)+random.uniform(-0.1,0.1); y=row*2.0*rad+random.uniform(-0.1,0.1)
        if random.random()<0.12: continue
        egg((x,y,random.uniform(-0.15,0.15)),rad*random.uniform(0.96,1.04)); k+=1
# ---- brightfield illumination: big emitter under the slide, black world
bl=bpy.data.objects.new('back',bpy.data.meshes.new('back')); sc.collection.objects.link(bl)
bm=bmesh.new(); bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=17); bm.to_mesh(bl.data); bm.free(); bl.location=(0.6,0.2,-40)
em,N,Lk=mat('light'); N.remove(N['Principled BSDF']); e=N.new('ShaderNodeEmission'); e.inputs['Color'].default_value=(0.93,0.92,0.95,1); e.inputs['Strength'].default_value=1.0
Lk.new(e.outputs[0],N['Material Output'].inputs['Surface']); bl.data.materials.append(em)
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[1].default_value=0.0
# ---- microscope camera: straight down, shallow focus on the eggs' mid plane
cd=bpy.data.cameras.new('cam'); cd.lens=85; cam=bpy.data.objects.new('cam',cd); sc.collection.objects.link(cam); cam.location=(0.6,0.2,24); sc.camera=cam
cd.dof.use_dof=True; cd.dof.focus_distance=24.0; cd.dof.aperture_fstop=1.4
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SPP; sc.cycles.use_denoising=True
sc.cycles.max_bounces=24; sc.cycles.transmission_bounces=24; sc.cycles.transparent_max_bounces=24; sc.cycles.volume_bounces=1
sc.render.resolution_x=RW; sc.render.resolution_y=int(RW*0.75)
sc.view_settings.view_transform='Standard'; sc.view_settings.look='None'
# chromatic fringe like a cheap objective
sc.use_nodes=True; ct=sc.node_tree; ct.nodes.clear(); rl=ct.nodes.new('CompositorNodeRLayers'); ld=ct.nodes.new('CompositorNodeLensdist'); ld.inputs['Dispersion'].default_value=0.02
co=ct.nodes.new('CompositorNodeComposite'); ct.links.new(rl.outputs['Image'],ld.inputs['Image']); ct.links.new(ld.outputs['Image'],co.inputs['Image'])
sc.render.filepath=OUT; bpy.ops.render.render(write_still=True); print('DONE')
