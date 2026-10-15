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

# ---- iPhone: rounded titanium body, black glass, rounded screen with iOS alarm wallpaper, Dynamic Island
def rrect(w,h,r,seg=10):
    pts=[]
    for cx,cy,a0 in ((w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)):
        for k in range(seg+1):
            a=math.radians(a0+90*k/seg); pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return pts
def unit_prism(name,w,h,r,t,S3,z0=0.0):
    bm=bmesh.new(); bot=[bm.verts.new((x/S3[0],y/S3[1],(z0-t/2)/S3[2])) for x,y in rrect(w,h,r)]; top=[bm.verts.new((x/S3[0],y/S3[1],(z0+t/2)/S3[2])) for x,y in rrect(w,h,r)]
    fb=bm.faces.new(bot[::-1]); ft=bm.faces.new(top); n=len(bot)
    for i in range(n): bm.faces.new((bot[i],bot[(i+1)%n],top[(i+1)%n],top[i]))
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); return me
BODY=(0.075,0.158,0.008)
body=bpy.data.objects['PHONE_Body']; me=unit_prism('IPHONE_BODY',0.0716,0.1476,0.0105,0.0078,BODY)
ti=bpy.data.materials.new('MAT_Titanium'); ti.use_nodes=True; tb=ti.node_tree.nodes['Principled BSDF']; tb.inputs['Base Color'].default_value=(0.42,0.40,0.37,1); tb.inputs['Metallic'].default_value=1.0; tb.inputs['Roughness'].default_value=0.32
gl=bpy.data.materials.new('MAT_BlackGlass'); gl.use_nodes=True; gb=gl.node_tree.nodes['Principled BSDF']; gb.inputs['Base Color'].default_value=(0.005,0.005,0.006,1); gb.inputs['Roughness'].default_value=0.04; gb.inputs['Coat Weight'].default_value=1.0
me.materials.append(ti); me.materials.append(gl)
for p in me.polygons:
    p.material_index=1 if abs(p.normal.z)>0.9 else 0
    p.use_smooth=abs(p.normal.z)<0.9
body.data=me
scr=bpy.data.objects['PHONE_Screen']; SCR=(0.069,0.15,1.0)
bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap')
vs=[bm.verts.new((x/SCR[0],y/SCR[1],0.0)) for x,y in rrect(0.0672,0.1445,0.0095)]
f=bm.faces.new(vs)
for lp in f.loops: lp[uv].uv=(lp.vert.co.x*SCR[0]/0.0672+0.5,lp.vert.co.y*SCR[1]/0.1445+0.5)
sm2=bpy.data.meshes.new('IPHONE_SCREEN'); bm.to_mesh(sm2); bm.free()
sm_=bpy.data.materials['MAT_Phone_Screen']; nt=sm_.node_tree; nt.nodes.clear(); o=nt.nodes.new('ShaderNodeOutputMaterial')
it=nt.nodes.new('ShaderNodeTexImage'); it.image=bpy.data.images.load(S+'tex/ios_alarm.png')
em=nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value=1.4; nt.links.new(it.outputs['Color'],em.inputs['Color'])
gs=nt.nodes.new('ShaderNodeBsdfGlossy'); gs.inputs['Roughness'].default_value=0.03; gs.inputs['Color'].default_value=(1,1,1,1)
fr=nt.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value=1.5; mx=nt.nodes.new('ShaderNodeMixShader'); nt.links.new(fr.outputs[0],mx.inputs[0]); nt.links.new(em.outputs[0],mx.inputs[1]); nt.links.new(gs.outputs[0],mx.inputs[2]); nt.links.new(mx.outputs[0],o.inputs['Surface'])
sm2.materials.append(sm_); scr.data=sm2
# Dynamic Island pill, parented to the body (built in the body's unit space)
di=unit_prism('IPHONE_ISLAND',0.0126,0.0037,0.00184,0.0003,BODY,z0=0.0041)
dio=bpy.data.objects.new('PHONE_Island',di); sc.collection.objects.link(dio); di.materials.append(gl)
for v in di.vertices: v.co.y+=0.0655/BODY[1]
dio.parent=body; dio.matrix_parent_inverse=Matrix.Identity(4)
# stop button: iOS orange, pulse ring soft white
sb=bpy.data.materials['MAT_Phone_Stop_Button']
if sb.use_nodes:
    for nd in sb.node_tree.nodes:
        if nd.type=='BSDF_PRINCIPLED': nd.inputs['Base Color'].default_value=(1.0,0.32,0.0,1); nd.inputs['Emission Color'].default_value=(1.0,0.32,0.0,1); nd.inputs['Emission Strength'].default_value=1.2
        if nd.type=='EMISSION': nd.inputs['Color'].default_value=(1.0,0.32,0.0,1)

# ---- underwater caustics + moving light shafts through the gobo (animated in drive via W)
gm=bpy.data.materials['MAT_Gobo']; nt=gm.node_tree; n=nt.nodes; l=nt.links; b=[x for x in n if x.type=='BSDF_PRINCIPLED'][0]
old_nz=[x for x in n if x.type=='TEX_NOISE'][0]; old_nz.name='GOBO_SHAFT'; old_nz.noise_dimensions='4D'
rp_old=[x for x in n if x.type=='VALTORGB'][0]
tc=n.new('ShaderNodeTexCoord'); mp=n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(140,110,1); l.new(tc.outputs['Object'],mp.inputs[0])
# light shafts: ~1 m patches in metres (the old noise ran on the 140 m plane's unit coords -> 100 m blobs, i.e. no shafts)
for lk in list(old_nz.inputs['Vector'].links): l.remove(lk)
l.new(mp.outputs[0],old_nz.inputs['Vector']); old_nz.inputs['Scale'].default_value=0.9; old_nz.inputs['Detail'].default_value=2
rp_old.color_ramp.elements[0].position=0.25; rp_old.color_ramp.elements[1].position=0.75; rp_old.color_ramp.elements[1].color=(0.55,0.55,0.55,1)
# physically-inspired caustics: light focuses where the wave surface curves like a lens.
# h(x,y,t) = animated 4D noise height field; intensity ~ 1/|1 + k*laplacian(h)| (finite differences, 5 taps)
D=0.03; K=0.075
def htap(dx,dy,tag):
    off=n.new('ShaderNodeVectorMath'); off.operation='ADD'; off.inputs[1].default_value=(dx,dy,0.0); l.new(mp.outputs[0],off.inputs[0])
    nz=n.new('ShaderNodeTexNoise'); nz.name='CAUSTIC_H_'+tag; nz.noise_dimensions='4D'; nz.inputs['Scale'].default_value=2.3; nz.inputs['Detail'].default_value=0.6; nz.inputs['Roughness'].default_value=0.45
    l.new(off.outputs[0],nz.inputs['Vector']); return nz.outputs['Fac']
hc=htap(0,0,'C'); hx1=htap(D,0,'X1'); hx2=htap(-D,0,'X2'); hy1=htap(0,D,'Y1'); hy2=htap(0,-D,'Y2')
def m(op,a,b=None,v=None):
    x=n.new('ShaderNodeMath'); x.operation=op
    l.new(a,x.inputs[0]) if not isinstance(a,(int,float)) else setattr(x.inputs[0],'default_value',a)
    if b is not None: l.new(b,x.inputs[1]) if not isinstance(b,(int,float)) else setattr(x.inputs[1],'default_value',b)
    return x.outputs[0]
s4=m('ADD',m('ADD',hx1,hx2),m('ADD',hy1,hy2)); lap=m('DIVIDE',m('SUBTRACT',s4,m('MULTIPLY',hc,4.0)),D*D)
J=m('MAXIMUM',m('ABSOLUTE',m('ADD',m('MULTIPLY',lap,K),1.0)),0.12)      # 1 + k*lap, clamped away from 0
I=m('DIVIDE',1.0,J)                                                      # focused intensity (~0.4 .. 8)
cr_node=n.new('ShaderNodeMapRange'); cr_node.interpolation_type='SMOOTHSTEP'; cr_node.inputs['From Min'].default_value=0.7; cr_node.inputs['From Max'].default_value=4.0; cr_node.inputs['To Min'].default_value=0.42; cr_node.inputs['To Max'].default_value=1.0
l.new(I,cr_node.inputs['Value']); cr=cr_node
inv=n.new('ShaderNodeMath'); inv.operation='SUBTRACT'; inv.inputs[0].default_value=1.0; l.new(rp_old.outputs[0],inv.inputs[1])     # shaft pass
mul=n.new('ShaderNodeMath'); mul.operation='MULTIPLY'; l.new(inv.outputs[0],mul.inputs[0]); l.new(cr.outputs[0],mul.inputs[1])
al=n.new('ShaderNodeMath'); al.operation='SUBTRACT'; al.inputs[0].default_value=1.0; l.new(mul.outputs[0],al.inputs[1]); l.new(al.outputs[0],b.inputs['Alpha'])
# ---- water surface: 4D noise so ripples move with time (W driven per frame)
vm=bpy.data.materials['MAT_WaterVolume']; pv=[x for x in vm.node_tree.nodes if x.type=='PRINCIPLED_VOLUME'][0]; pv.inputs['Anisotropy'].default_value=0.82   # strong forward scatter -> visible shafts
wm=bpy.data.materials['MAT_Pond_Water_Surface']
for i,nd in enumerate([x for x in wm.node_tree.nodes if x.type=='TEX_NOISE']):
    nd.noise_dimensions='4D'; nd.name='WAVE_%d'%i
bpy.ops.wm.save_as_mainfile(filepath=S+'film/film.blend'); print('POLISH_OK')
