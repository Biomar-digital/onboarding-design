# Water detail: full-size pools for bubbles / splash drops / impact rings / pellets, proper ring geometry,
# water-like materials, and suspended particles (plankton/silt) for the underwater shots.
import bpy, math, random, bmesh
from mathutils import Vector, Matrix
S='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/'
bpy.ops.wm.open_mainfile(filepath=S+'film/film.blend'); sc=bpy.context.scene; random.seed(5)
def grow(prefix,n):
    src=bpy.data.objects[prefix+'000']; have=len([o for o in bpy.data.objects if o.name.startswith(prefix)])
    for i in range(have,n):
        q=src.copy(); sc.collection.objects.link(q); q.name='%s%03d'%(prefix,i) if i<1000 else '%s%04d'%(prefix,i); q.hide_render=True
grow('BUB_',800); grow('DROP_',900); grow('PEL_',1200)
# rings: a soft torus lying in the water plane (three XZ -> blender local XY), replacing the edge-only circle
bm=bmesh.new(); bmesh.ops.create_circle(bm,segments=8,radius=0.07)
me=bpy.data.meshes.new('RING_ME'); tor=bpy.data.objects.new('tmp',me)
# ripples spread to a few cm around each 3 mm pellet: two concentric wave crests, very low
ts=[]
for R,r in ((7.0,0.28),(4.6,0.2)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R,minor_radius=r,major_segments=96,minor_segments=8); ts.append(bpy.context.object)
bpy.ops.object.select_all(action='DESELECT'); [x.select_set(True) for x in ts]; bpy.context.view_layer.objects.active=ts[0]; bpy.ops.object.join(); t=bpy.context.object
t.data.transform(Matrix.Diagonal((1,1,0.0025,1))); ringme=t.data; bpy.data.objects.remove(t)
for p in ringme.polygons: p.use_smooth=True
rm=bpy.data.materials.new('MAT_Ripple'); rm.use_nodes=True; b=rm.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(0.55,0.62,0.55,1); b.inputs['Roughness'].default_value=0.02; b.inputs['Transmission Weight'].default_value=1.0; b.inputs['IOR'].default_value=1.333
nt=rm.node_tree; out=nt.nodes['Material Output']; b=nt.nodes['Principled BSDF']; b.inputs['Transmission Weight'].default_value=0.0; b.inputs['Base Color'].default_value=(0.05,0.07,0.05,1)
tr=nt.nodes.new('ShaderNodeBsdfTransparent'); mx=nt.nodes.new('ShaderNodeMixShader'); oi=nt.nodes.new('ShaderNodeObjectInfo')
fr=nt.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value=1.333; mul=nt.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'
sep=nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(oi.outputs['Color'],sep.inputs[0]); nt.links.new(sep.outputs[0],mul.inputs[0]); mul2=nt.nodes.new('ShaderNodeMath'); mul2.operation='MULTIPLY'; mul2.inputs[1].default_value=1.0
nt.links.new(fr.outputs[0],mul2.inputs[0]); nt.links.new(mul2.outputs[0],mul.inputs[1]); mx2=nt.nodes.new('ShaderNodeMath'); mx2.operation='MAXIMUM'; mx2.inputs[1].default_value=0.0
nt.links.new(mul.outputs[0],mx.inputs[0]); nt.links.new(tr.outputs[0],mx.inputs[1]); nt.links.new(b.outputs[0],mx.inputs[2]); nt.links.new(mx.outputs[0],out.inputs[0])
rm.blend_method='BLEND' if hasattr(rm,'blend_method') else None
ringme.materials.append(rm)
have=len([o for o in bpy.data.objects if o.name.startswith('RING_') and o.name!='RING_SRC'])
src=bpy.data.objects['RING_000']
for i in range(have,400):
    q=src.copy(); sc.collection.objects.link(q); q.name='RING_%03d'%i
for o in bpy.data.objects:
    if o.name.startswith('RING_'): o.data=ringme; o.hide_render=True; o.visible_shadow=False
print('ring check: previs ring geometry assumed in XZ plane; mesh now flat in three XZ via local XZ data')
# bubbles: air in water (IOR<1) with a faint bright rim so they read against murky water
bm_=bpy.data.materials['Bubble']; nt=bm_.node_tree; b=nt.nodes['Principled BSDF']
b.inputs['IOR'].default_value=0.75; b.inputs['Roughness'].default_value=0.0; b.inputs['Transmission Weight'].default_value=1.0
lw=nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value=0.25; em=nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value=(0.85,0.95,0.9,1)
mul=nt.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'; mul.inputs[1].default_value=0.0; nt.links.new(lw.outputs['Facing'],mul.inputs[0]); nt.links.new(mul.outputs[0],em.inputs['Strength'])
ad=nt.nodes.new('ShaderNodeAddShader'); out=nt.nodes['Material Output']; nt.links.new(b.outputs[0],ad.inputs[0]); nt.links.new(em.outputs[0],ad.inputs[1]); nt.links.new(ad.outputs[0],out.inputs[0])
sm=bpy.data.objects['SPH_SRC'].data
import bmesh as _bm
_b=_bm.new(); _bm.ops.create_uvsphere(_b,u_segments=32,v_segments=16,radius=1.0); _b.to_mesh(sm); _b.free()
for p in sm.polygons: p.use_smooth=True
for o in bpy.data.objects:
    if o.name.startswith(('BUB_','DROP_')): o.visible_shadow=False
# suspended particles: tiny flecks instanced on random verts in a slab under the surface (follows the camera per frame in drive)
pm=bpy.data.meshes.new('MOTES'); vs=[(random.uniform(-2.0,1.6),random.uniform(2.8,7.5),random.uniform(-1.45,-0.03)) for _ in range(30000)]
pm.from_pydata(vs,[],[]); mo=bpy.data.objects.new('MOTES',pm); sc.collection.objects.link(mo); mo.instance_type='VERTS'; mo.show_instancer_for_render=False
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=0.00035); f=bpy.context.object; f.name='MOTE'; f.parent=mo
mm=bpy.data.materials.new('MAT_Mote'); mm.use_nodes=True; b=mm.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.16,0.15,0.09,1); b.inputs['Roughness'].default_value=0.9
b.inputs['Emission Strength'].default_value=0.0; f.data.materials.append(mm); f.visible_shadow=False
mo.hide_render=True

# impact crowns: thin flared water wall with spiky rim, placed on young rings (radius in ring units, height 1 -> scaled per frame)
import math as _m
cv=[]; cf=[]; N=28
for i in range(N):
    a=2*_m.pi*i/N; cv.append((0.42*_m.cos(a),0.42*_m.sin(a),0.0))
for i in range(N):
    a=2*_m.pi*i/N; r=0.78+0.08*((i%2)); z=1.0+(0.45 if i%2==0 else 0.0); cv.append((r*_m.cos(a),r*_m.sin(a),z))
for i in range(N):
    j=(i+1)%N; cf.append((i,j,N+j,N+i))
cm=bpy.data.meshes.new('CROWN_ME'); cm.from_pydata(cv,[],cf); cm.materials.append(bpy.data.materials['Drop'])
for p in cm.polygons: p.use_smooth=True
for i in range(220):
    o=bpy.data.objects.new('CROWN_%03d'%i,cm); sc.collection.objects.link(o); o.hide_render=True; o.visible_shadow=False
# pellet surface: extruded feed, matte, pitted, slightly mottled
pm=bpy.data.objects['PEL_000'].active_material
if pm and pm.use_nodes:
    nt=pm.node_tree; b=[x for x in nt.nodes if x.type=='BSDF_PRINCIPLED'][0]; L=nt.links
    tc=nt.nodes.new('ShaderNodeTexCoord'); nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=9.0; nz.inputs['Detail'].default_value=10; L.new(tc.outputs['Object'],nz.inputs['Vector'])
    vo=nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value=22; L.new(tc.outputs['Object'],vo.inputs['Vector'])
    rp=nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].color=(0.13,0.07,0.035,1); rp.color_ramp.elements[1].color=(0.30,0.18,0.09,1); L.new(nz.outputs['Fac'],rp.inputs[0])
    L.new(rp.outputs[0],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.85
    for nm in ('Specular IOR Level',):
        if nm in b.inputs: b.inputs[nm].default_value=0.3
    bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.6; bp.inputs['Distance'].default_value=0.05
    mx=nt.nodes.new('ShaderNodeMath'); mx.operation='ADD'; L.new(nz.outputs['Fac'],mx.inputs[0]); L.new(vo.outputs['Distance'],mx.inputs[1])
    L.new(mx.outputs[0],bp.inputs['Height']); L.new(bp.outputs[0],b.inputs['Normal'])
bpy.ops.wm.save_as_mainfile(filepath=S+'film/film.blend'); print('FX_OK')
