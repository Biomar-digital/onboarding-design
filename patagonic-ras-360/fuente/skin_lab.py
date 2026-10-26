# Close-up skin comparison under the hall's water and light: original material vs salmon_skin().
import bpy, bmesh, math, sys, os, mathutils
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=sys.argv[sys.argv.index('--')+1]
src=open(os.path.join(HERE,'hall.py')).read()
bpy.ops.wm.read_factory_settings(use_empty=True); sc=bpy.context.scene
def mk(name,build):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); build(bm); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); sc.collection.objects.link(ob); return ob
box=mk('W',lambda bm: bmesh.ops.create_cube(bm,size=1)); box.scale=(400,400,16)
vm=bpy.data.materials.new('w'); vm.use_nodes=True; vn=vm.node_tree; vn.nodes.remove(vn.nodes['Principled BSDF'])
v=vn.nodes.new('ShaderNodeVolumePrincipled'); v.inputs['Color'].default_value=(0.04,0.22,0.52,1); v.inputs['Density'].default_value=0.075
v.inputs['Anisotropy'].default_value=0.75; v.inputs['Absorption Color'].default_value=(0.12,0.42,0.82,1)
vn.links.new(v.outputs[0],vn.nodes['Material Output'].inputs['Volume']); box.data.materials.append(vm)
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.02,0.1,0.26,1)
sky=mk('sky',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=400)); sky.location=(0,0,7.9)
km=bpy.data.materials.new('k'); km.use_nodes=True; kn=km.node_tree; kn.nodes.remove(kn.nodes['Principled BSDF'])
e=kn.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value=(1.0,1.25,1.5,1); e.inputs['Strength'].default_value=1.0
kn.links.new(e.outputs[0],kn.nodes['Material Output'].inputs['Surface']); sky.data.materials.append(km); sky.visible_shadow=False
sun=bpy.data.lights.new('s','SUN'); sun.energy=34; sun.angle=math.radians(2); so=bpy.data.objects.new('s',sun); sc.collection.objects.link(so); so.rotation_euler=(math.radians(-30),math.radians(25),math.radians(-20))
cam=bpy.data.cameras.new('c'); cam.lens=35; co=bpy.data.objects.new('c',cam); sc.collection.objects.link(co); co.rotation_euler=(math.radians(90),0,0); sc.camera=co
def load(tag,skin):
    before=set(bpy.data.objects); mats=set(bpy.data.materials)
    bpy.ops.import_scene.gltf(filepath=os.path.join(HERE,'fish_feeding.glb'))
    new=[o for o in bpy.data.objects if o not in before]
    for o in new:
        if o.name.startswith('Icosphere'): o.hide_render=True
    body=max([o for o in new if o.type=='MESH'],key=lambda o:len(o.data.vertices))
    m=[x for x in bpy.data.materials if x not in mats][0]; m.name='Fish_Shd' if skin else 'Fish_orig'
    if skin:
        ns={'bpy':bpy,'os':os}; exec(src[src.index('def salmon_skin'):src.index("if not os.environ.get('RAS_ORIGINAL_SKIN')")],ns)
        bb=[body.matrix_world@mathutils.Vector(c) for c in body.bound_box]; L=max(max(v[i] for v in bb)-min(v[i] for v in bb) for i in range(3)); ns['salmon_skin'](L)
        if os.environ.get('DBG'):
            nt=bpy.data.materials['Fish_Shd'].node_tree; em=nt.nodes.new('ShaderNodeEmission')
            sp=[n for n in nt.nodes if n.bl_idname=='ShaderNodeMix' and n.data_type=='RGBA'][-1].inputs['Factor'].links[0].from_socket
            nt.links.new(sp,em.inputs['Strength']); nt.links.new(em.outputs[0],nt.nodes['Material Output'].inputs['Surface'])
    root=bpy.data.objects.new('R'+tag,None); sc.collection.objects.link(root)
    for o in new:
        if o.parent is None: o.parent=root
    bpy.context.view_layer.update(); bb=[body.matrix_world@mathutils.Vector(c) for c in body.bound_box]
    return root,max(max(v[i] for v in bb)-min(v[i] for v in bb) for i in range(3))
def dup(root):
    m={}
    for o in [root]+list(root.children_recursive):
        c=o.copy(); sc.collection.objects.link(c); m[o]=c
    for o,c in m.items():
        if o.parent in m: c.parent=m[o.parent]
        for md in c.modifiers:
            if md.type=='ARMATURE' and md.object in m: md.object=m[md.object]
    return m[root]
for side,skin in ((-1,False),(1,True)):
    r0,L=load(str(side),skin)
    for k,roll in enumerate((0,25,50)):
        r=r0 if k==0 else dup(r0); s=0.7/L; r.scale=(s,s,s)
        r.location=(side*0.55,2.2+0.15*k,0.42-0.42*k); r.rotation_euler=(0,math.radians(roll*side*-1),math.radians(90 if side<0 else -90))
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=64; sc.cycles.use_denoising=True
sc.cycles.max_bounces=8; sc.cycles.glossy_bounces=4; sc.cycles.volume_bounces=0
sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Punchy'
sc.render.resolution_x=1400; sc.render.resolution_y=800; sc.render.filepath=OUT; bpy.ops.render.render(write_still=True); print('DONE')
