# Bubble look-dev: same water/light as the hall, 4 shader variants side by side, close and mid distance.
import bpy, bmesh, math, sys, os
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); import bubbles
OUT=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True); sc=bpy.context.scene
def mk(name,build):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); build(bm); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); sc.collection.objects.link(ob); return ob
box=mk('W',lambda bm: bmesh.ops.create_cube(bm,size=1)); box.scale=(400,400,16); box.location=(0,0,0)
vm=bpy.data.materials.new('w'); vm.use_nodes=True; vn=vm.node_tree; vn.nodes.remove(vn.nodes['Principled BSDF'])
v=vn.nodes.new('ShaderNodeVolumePrincipled'); v.inputs['Color'].default_value=(0.04,0.22,0.52,1); v.inputs['Density'].default_value=0.075
v.inputs['Anisotropy'].default_value=0.75; v.inputs['Absorption Color'].default_value=(0.12,0.42,0.82,1)
vn.links.new(v.outputs[0],vn.nodes['Material Output'].inputs['Volume']); box.data.materials.append(vm)
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.02,0.1,0.26,1)
sky=mk('sky',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=400)); sky.location=(0,0,7.9)
km=bpy.data.materials.new('k'); km.use_nodes=True; kn=km.node_tree; kn.nodes.remove(kn.nodes['Principled BSDF'])
e=kn.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value=(1.0,1.25,1.5,1); e.inputs['Strength'].default_value=1.0
kn.links.new(e.outputs[0],kn.nodes['Material Output'].inputs['Surface']); sky.data.materials.append(km)
fl=mk('fl',lambda bm: bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=400)); fl.location=(0,0,-7.9)
sun=bpy.data.lights.new('s','SUN'); sun.energy=34; sun.angle=math.radians(2); so=bpy.data.objects.new('s',sun); sc.collection.objects.link(so); so.rotation_euler=(math.radians(-30),math.radians(25),math.radians(-20))
cam=bpy.data.cameras.new('c'); cam.lens=50; co=bpy.data.objects.new('c',cam); sc.collection.objects.link(co); co.rotation_euler=(math.radians(90),0,0); sc.camera=co
def M(kind):
    m=bpy.data.materials.new(kind); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links; out=N['Material Output']
    if kind=='A_actual': return bubbles.material()
    N.remove(N['Principled BSDF'])
    if kind=='B_vidrio_075':
        g=N.new('ShaderNodeBsdfGlass'); g.inputs['IOR'].default_value=1/1.33; g.inputs['Roughness'].default_value=0.0; L.new(g.outputs[0],out.inputs['Surface'])
    if kind=='C_normales_inv':
        g=N.new('ShaderNodeBsdfGlass'); g.inputs['IOR'].default_value=1.33; g.inputs['Roughness'].default_value=0.0; L.new(g.outputs[0],out.inputs['Surface']); m['flip']=1
    if kind=='D_fisico_TIR':
        # see-through refraction (IOR 0.752) + explicit total internal reflection mirror past the critical angle
        g=N.new('ShaderNodeBsdfRefraction'); g.inputs['IOR'].default_value=1/1.33; g.inputs['Roughness'].default_value=0.0
        r=N.new('ShaderNodeBsdfGlossy'); r.inputs['Roughness'].default_value=0.0
        lw=N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value=0.5
        cr=N.new('ShaderNodeMapRange'); L.new(lw.outputs['Facing'],cr.inputs[0]); cr.inputs[1].default_value=0.25; cr.inputs[2].default_value=0.45   # ~ sin(48.8 deg) critical angle
        mx=N.new('ShaderNodeMixShader'); L.new(cr.outputs[0],mx.inputs[0]); L.new(g.outputs[0],mx.inputs[1]); L.new(r.outputs[0],mx.inputs[2]); L.new(mx.outputs[0],out.inputs['Surface'])
    return m
kinds=['A_actual','B_vidrio_075','C_normales_inv','D_fisico_TIR']
for i,k in enumerate(kinds):
    m=M(k)
    for j,(d,r) in enumerate(((0.35,0.006),(0.35,0.003),(1.2,0.008),(1.2,0.004))):
        def b(bm): bmesh.ops.create_uvsphere(bm,u_segments=32,v_segments=16,radius=1.0)
        o=mk(f'b{i}{j}',b); o.data.materials.append(m)
        for p in o.data.polygons: p.use_smooth=True
        if m.get('flip'):
            for p in o.data.polygons: p.flip()
        x=(i-1.5)*0.075*(d/0.35); z=(0.03 if j%2==0 else -0.03)*(d/0.35)
        o.location=(x,d,z); o.scale=(r,r,r*(0.85 if r>0.005 else 1)); o.visible_shadow=False
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=128; sc.cycles.use_denoising=False
sc.cycles.max_bounces=16; sc.cycles.glossy_bounces=12; sc.cycles.transmission_bounces=16; sc.cycles.transparent_max_bounces=16; sc.cycles.volume_bounces=0
sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Punchy'
sc.render.resolution_x=1600; sc.render.resolution_y=500; cam.sensor_width=36
sc.render.filepath=OUT; bpy.ops.render.render(write_still=True); print('DONE')
