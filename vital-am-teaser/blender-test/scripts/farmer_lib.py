import bpy, math, bmesh
from mathutils import Vector, Euler, Matrix
FARMER='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/hf/farmer_rig.glb'
def load_farmer(imp):
    objs=imp(FARMER)
    for o in list(objs):
        if o.name.startswith('Icosphere'): bpy.data.objects.remove(o); objs.remove(o)
    arm=[o for o in objs if o.type=='ARMATURE'][0]; body=[o for o in objs if o.type=='MESH'][0]
    if arm.animation_data: arm.animation_data.action=None
    return arm, body
def pose(arm, rots):
    # rots: {bone: (x,y,z) degrees} in bone-local space
    for pb in arm.pose.bones: pb.rotation_mode='XYZ'; pb.rotation_euler=(0,0,0)
    for b,(x,y,z) in rots.items(): arm.pose.bones[b].rotation_euler=(math.radians(x),math.radians(y),math.radians(z))
    bpy.context.view_layer.update()
def del_faces(o,pred):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update(); fs=[f for f in bm.faces if pred(f)]
    bmesh.ops.delete(bm,geom=fs,context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update()
def blue_mat(name='BluePlastic',rgb=(0.02,0.16,0.55)):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=0.35; return m
def make_scoop(arm, hand='RightHand'):
    # small feed scoop: open cup (~12 cm) + handle (~14 cm), parented to the hand bone
    m=blue_mat('Scoop',(0.03,0.22,0.62))
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=0.055,depth=0.11); cup=bpy.context.object
    del_faces(cup, lambda f: f.normal.z>0.9)
    # slant-cut the cup lip so it reads as a feed scoop, not a mug
    for v in cup.data.vertices:
        if v.co.z>0: v.co.z = v.co.z - (v.co.y+0.055)*0.45
    sol=cup.modifiers.new('S','SOLIDIFY'); sol.thickness=0.004
    cup.rotation_euler=(math.radians(90),0,0); cup.location=(0,0.16,0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=0.013,depth=0.15,location=(0,0.06,0)); h=bpy.context.object; h.rotation_euler=(math.radians(90),0,0)
    for o in (cup,h): o.data.materials.append(m)
    bpy.ops.object.empty_add(location=(0,0,0)); root=bpy.context.object; root.name='ScoopRoot'
    for o in (cup,h): o.parent=root
    attach_to_hand(root,arm,hand); return root
def attach_to_hand(obj,arm,hand='RightHand',off=(0,0.06,0.0),rot=(0,0,0)):
    # world-space placement on the posed hand bone (armature is cm-scaled, so strip scale)
    bpy.context.view_layer.update()
    M=arm.matrix_world@arm.pose.bones[hand].matrix
    loc,q,_=M.decompose(); R=q.to_matrix().to_4x4()
    obj.matrix_world=Matrix.Translation(loc)@R@Matrix.Translation(Vector(off))@Euler([math.radians(a) for a in rot]).to_matrix().to_4x4()
def make_bucket(loc):
    m=blue_mat('Bucket',(0.04,0.18,0.48))
    bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=0.15,radius2=0.18,depth=0.38,location=(loc[0],loc[1],loc[2]+0.19)); b=bpy.context.object
    del_faces(b, lambda f: f.normal.z>0.9)
    b.modifiers.new('S','SOLIDIFY').thickness=0.006; b.data.materials.append(m)
    # feed inside
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=0.172,depth=0.01,location=(loc[0],loc[1],loc[2]+0.30)); f=bpy.context.object
    fm=bpy.data.materials.new('FeedTop'); fm.use_nodes=True; nb=fm.node_tree.nodes['Principled BSDF']; nb.inputs['Base Color'].default_value=(0.20,0.11,0.05,1); nb.inputs['Roughness'].default_value=0.9
    nz=fm.node_tree.nodes.new('ShaderNodeTexVoronoi'); nz.inputs['Scale'].default_value=300; bp=fm.node_tree.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.6
    fm.node_tree.links.new(nz.outputs['Distance'],bp.inputs['Height']); fm.node_tree.links.new(bp.outputs['Normal'],nb.inputs['Normal'])
    f.data.materials.append(fm); return b
