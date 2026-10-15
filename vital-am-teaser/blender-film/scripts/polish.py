# Standard flat feed scoop (like the client photo) + a touch of light on the shrimp.
import bpy, bmesh, math
from mathutils import Vector, Matrix
S='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/'
bpy.ops.wm.open_mainfile(filepath=S+'film/film.blend'); sc=bpy.context.scene
root=bpy.data.objects['SCOOP']
for c in list(root.children): bpy.data.objects.remove(c)
# ---- scoop in root-local coords: handle along +Y (grip centre at y=0.06), shovel continues forward along +Y, floor at z=0, walls up +z
sm=bpy.data.materials.new('MAT_ScoopPurple'); sm.use_nodes=True; b=sm.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(0.10,0.06,0.62,1); b.inputs['Roughness'].default_value=0.38; b.inputs['Coat Weight'].default_value=0.2
bm=bmesh.new()
y0,y1=0.13,0.33; wb,wf=0.045,0.07; hb,hf=0.055,0.012     # back/front half-width, back/front wall height (front open & low)
fl=[Vector((-wb,y0,0)),Vector((wb,y0,0)),Vector((wf,y1,0)),Vector((-wf,y1,0))]
top=[Vector((-wb*1.08,y0,hb)),Vector((wb*1.08,y0,hb)),Vector((wf*1.12,y1,hf)),Vector((-wf*1.12,y1,hf))]
V=[bm.verts.new(p) for p in fl+top]
bm.faces.new((V[0],V[1],V[2],V[3]))                 # floor
bm.faces.new((V[0],V[1],V[5],V[4]))                 # back wall
bm.faces.new((V[1],V[2],V[6],V[5]))                 # right wall (tapers to the open front)
bm.faces.new((V[3],V[0],V[4],V[7]))                 # left wall
me=bpy.data.meshes.new('SCOOP_BODY'); bm.to_mesh(me); bm.free()
body=bpy.data.objects.new('SCOOP_BODY',me); sc.collection.objects.link(body); me.materials.append(sm)
so=body.modifiers.new('S','SOLIDIFY'); so.thickness=0.004; so.offset=0; bv=body.modifiers.new('B','BEVEL'); bv.width=0.003; bv.segments=2
# straight handle in line with the shovel, slightly raised, with a hanging-hole tip
bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=0.012,depth=0.15,location=(0,0.06,0.03)); h=bpy.context.object; h.name='SCOOP_HANDLE'
h.rotation_euler=(math.radians(90),0,0); h.data.materials.append(sm)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0.125,0.02)); nk=bpy.context.object; nk.name='SCOOP_NECK'; nk.scale=(0.02,0.03,0.012); nk.data.materials.append(sm)
# feed load (heap of pellets) inside the shovel; drive hides it after the release
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,0.23,0.022)); ld=bpy.context.object; ld.name='SCOOP_LOAD'; ld.scale=(0.11,0.19,1)
sd=ld.modifiers.new('sub','SUBSURF'); sd.levels=3; sd.render_levels=3; sd.subdivision_type='SIMPLE'
dt=bpy.data.textures.new('HEAP','CLOUDS'); dt.noise_scale=0.05; dp=ld.modifiers.new('d','DISPLACE'); dp.texture=dt; dp.strength=0.012
ld.data.materials.append(bpy.data.materials['MAT_FeedHeap'])
bpy.context.view_layer.update()
for o in (body,h,nk,ld):
    mw=o.matrix_world.copy(); o.parent=root; o.matrix_parent_inverse=Matrix.Identity(4); o.matrix_basis=mw
# ---- shrimp: a little light of their own (soft self-glow + bright rim so they read against the water)
mt=bpy.data.objects['SHRM_000'].data.materials[0]; nt=mt.node_tree; n=nt.nodes; l=nt.links
bs=[x for x in n if x.type=='BSDF_PRINCIPLED'][0]; bs.inputs['Emission Strength'].default_value=0.07; bs.inputs['Emission Color'].default_value=(0.75,0.78,0.7,1)
out=[x for x in n if x.type=='OUTPUT_MATERIAL'][0]; src=out.inputs['Surface'].links[0].from_socket
lw=n.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value=0.35; em=n.new('ShaderNodeEmission'); em.inputs['Color'].default_value=(0.9,0.95,0.9,1)
mu=n.new('ShaderNodeMath'); mu.operation='MULTIPLY'; mu.inputs[1].default_value=0.32; l.new(lw.outputs['Fresnel'],mu.inputs[0]); l.new(mu.outputs[0],em.inputs['Strength'])
ad=n.new('ShaderNodeAddShader'); l.new(src,ad.inputs[0]); l.new(em.outputs[0],ad.inputs[1]); l.new(ad.outputs[0],out.inputs['Surface'])
bpy.ops.wm.save_as_mainfile(filepath=S+'film/film.blend'); print('POLISH_OK')
