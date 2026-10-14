# Vegetation pass: leaf-card trees replace the blob tree line, 3D grass tiles on the dyke tops near camera,
# painted-metal aerator motors. Runs after hf_assets.py.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
S='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/'
bpy.ops.wm.open_mainfile(filepath=S+'film/film.blend'); sc=bpy.context.scene; rnd=random.Random(21)
def colattr(me,name='Col'):
    return me.color_attributes.new(name,'FLOAT_COLOR','CORNER')
# ---------- materials
def leaf_mat(name,translucent=0.35):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; n=nt.nodes; L=nt.links; n.clear()
    out=n.new('ShaderNodeOutputMaterial'); b=n.new('ShaderNodeBsdfPrincipled'); at=n.new('ShaderNodeAttribute'); at.attribute_name='Col'
    L.new(at.outputs['Color'],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.55
    tl=n.new('ShaderNodeBsdfTranslucent'); L.new(at.outputs['Color'],tl.inputs['Color']); mx=n.new('ShaderNodeMixShader'); mx.inputs[0].default_value=translucent
    L.new(b.outputs[0],mx.inputs[1]); L.new(tl.outputs[0],mx.inputs[2]); L.new(mx.outputs[0],out.inputs[0]); return m
leafm=leaf_mat('MAT_Leaf',0.3); grassm=leaf_mat('MAT_GrassBlade',0.4)
barkm=bpy.data.materials.new('MAT_Bark'); barkm.use_nodes=True; bb=barkm.node_tree.nodes['Principled BSDF']; bb.inputs['Base Color'].default_value=(0.09,0.07,0.05,1); bb.inputs['Roughness'].default_value=0.9
# ---------- trees
def make_tree(seed):
    r=random.Random(seed); bm=bmesh.new(); cl=bm.loops.layers.float_color.new('Col')
    H=r.uniform(7,11); cr=r.uniform(3.2,4.6)
    # trunk + a few limbs
    def limb(p0,p1,r0,r1):
        d=(p1-p0); q=d.to_track_quat('Z','Y'); ln=d.length
        ret=bmesh.ops.create_cone(bm,cap_ends=False,segments=7,radius1=r0,radius2=r1,depth=ln)
        for v in ret['verts']: v.co=p0+(q@(v.co+Vector((0,0,ln/2))))
        for f in {f for v in ret['verts'] for f in v.link_faces}: f.material_index=1
    base=Vector((0,0,0)); top=Vector((r.uniform(-0.4,0.4),r.uniform(-0.4,0.4),H*0.62)); limb(base,top,0.28,0.16)
    clumps=[]
    for k in range(r.randint(5,8)):
        a=r.uniform(0,6.28); rr=r.uniform(0.3,1.0)*cr*0.6
        c=Vector((math.cos(a)*rr,math.sin(a)*rr,H*r.uniform(0.62,0.9))); s=r.uniform(0.45,0.7)*cr
        clumps.append((c,s)); limb(top,c,0.12,0.05)
    clumps.append((Vector((0,0,H*0.82)),cr*0.8))
    for c,s in clumps:
        n=int(1150*(s/cr)**2)+250
        tint=r.uniform(-0.03,0.03)
        for i in range(n):
            dv=Vector((r.gauss(0,1),r.gauss(0,1),r.gauss(0,1))).normalized(); dv.z*=0.75
            p=c+dv*s*(r.uniform(0.82,1.0) if r.random()<0.8 else r.uniform(0.3,0.8))
            ln=r.uniform(0.2,0.32); wd=ln*0.42
            q=Vector((r.gauss(0,1),r.gauss(0,1),r.gauss(0,1))).normalized(); t=q.cross(dv).normalized(); bnorm=dv.cross(t)
            vs=[bm.verts.new(p),bm.verts.new(p+t*ln*0.5+bnorm*wd*0.5),bm.verts.new(p+t*ln),bm.verts.new(p+t*ln*0.5-bnorm*wd*0.5)]
            f=bm.faces.new(vs); f.material_index=0
            sun=max(0.0,dv.z*0.5+0.5)    # outer/top leaves lighter
            col=(0.035+0.05*sun+tint, 0.075+0.07*sun+r.uniform(-0.015,0.02), 0.022+0.015*sun, 1)
            for lp in f.loops: lp[cl]=col
    me=bpy.data.meshes.new('TREE_ME_%d'%seed); bm.to_mesh(me); bm.free()
    me.materials.append(leafm); me.materials.append(barkm); return me
trees=[make_tree(s) for s in range(5)]
old=[o for o in bpy.data.objects if o.name.startswith('TREE_')]
for i,o in enumerate(old):
    p=o.location.copy(); sz=max(o.dimensions.x,o.dimensions.y)
    for k in range(3):   # three trees per old blob -> a continuous, layered tree line
        t=bpy.data.objects.new('TREE_V_%03d_%d'%(i,k),trees[(i+k*2)%5]); sc.collection.objects.link(t)
        s=rnd.uniform(1.2,1.9); j=Vector((rnd.uniform(-7,7),rnd.uniform(-7,7),0)) if k else Vector()
        t.matrix_world=Matrix.Translation((p.x+j.x,p.y+j.y,0.8))@Matrix.Rotation(rnd.uniform(0,6.28),4,'Z')@Matrix.Scale(s,4)
for o in old: bpy.data.objects.remove(o)
# ---------- grass tiles on dyke tops / ground near the action
def grass_tile(seed,size=1.4,n=1700):
    r=random.Random(seed); bm=bmesh.new(); cl=bm.loops.layers.float_color.new('Col')
    for i in range(n):
        x=r.uniform(-size/2,size/2); y=r.uniform(-size/2,size/2); h=r.uniform(0.07,0.26)*(1.4 if r.random()<0.1 else 1)
        a=r.uniform(0,6.28); d=Vector((math.cos(a),math.sin(a),0)); side=Vector((-d.y,d.x,0)); w=r.uniform(0.004,0.007); lean=r.uniform(0.15,0.55)
        pts=[]
        for k,(t,wk) in enumerate(((0,1),(0.45,0.8),(0.8,0.45))):
            c=Vector((x,y,0))+Vector((0,0,h*t))+d*(lean*h*t*t)
            pts.append((bm.verts.new(c+side*w*wk),bm.verts.new(c-side*w*wk)))
        tip=bm.verts.new(Vector((x,y,0))+Vector((0,0,h))+d*lean*h)
        dry=r.random()
        col=((0.10,0.12,0.035,1) if dry<0.65 else (0.20,0.18,0.07,1)) if r.random()<0.9 else (0.06,0.09,0.03,1)
        fs=[bm.faces.new((pts[0][0],pts[0][1],pts[1][1],pts[1][0])),bm.faces.new((pts[1][0],pts[1][1],pts[2][1],pts[2][0])),bm.faces.new((pts[2][0],pts[2][1],tip))]
        for k,f in enumerate(fs):
            m=0.55+0.25*k
            for lp in f.loops: lp[cl]=(col[0]*m*1.3,col[1]*m*1.3,col[2]*m,1)
    me=bpy.data.meshes.new('GRASS_ME_%d'%seed); bm.to_mesh(me); bm.free(); me.materials.append(grassm); return me
tiles=[grass_tile(s) for s in range(4)]
dg=bpy.context.evaluated_depsgraph_get(); cnt=0
centres=[(Vector((0,9.8)),26.0),(Vector((0.2,9.5)),26.0)]
xs=[x*1.3 for x in range(-24,25)]
for x in xs:
    for y0 in range(-14,30):
        y=y0*1.3+rnd.uniform(-0.3,0.3); xx=x+rnd.uniform(-0.3,0.3)
        if min((Vector((xx,y))-c).length-rad for c,rad in centres)>0: continue
        ok,loc,nor,idx,ob,mtx=sc.ray_cast(dg,Vector((xx,y,20)),Vector((0,0,-1)))
        if not ok or nor.z<0.8 or loc.z<0.55 or not ob.name.startswith(('POND_Basin','GROUND_FAR','SET_Dyke','ENV_Dyke')): continue
        g=bpy.data.objects.new('GRASS_%04d'%cnt,tiles[cnt%4]); sc.collection.objects.link(g); cnt+=1
        g.matrix_world=Matrix.Translation(loc-Vector((0,0,0.005)))@Matrix.Rotation(rnd.uniform(0,6.28),4,'Z')@Matrix.Scale(rnd.uniform(0.9,1.15),4)
        g.visible_shadow=True
print('GRASS_TILES',cnt)
# ---------- aerator motors: bevelled painted metal instead of a raw grey cube
mm=bpy.data.materials.new('MAT_MotorPaint'); mm.use_nodes=True; nt=mm.node_tree; b=nt.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.10,0.16,0.13,1); b.inputs['Metallic'].default_value=0.6; b.inputs['Roughness'].default_value=0.42
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=40; bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.05; nt.links.new(nz.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs[0],b.inputs['Normal'])
for o in bpy.data.objects:
    if o.type=='MESH' and 'Motor' in o.name:
        bv=o.modifiers.new('bev','BEVEL'); bv.width=0.03; bv.segments=3; o.data.materials.clear(); o.data.materials.append(mm)
bpy.ops.wm.save_as_mainfile(filepath=S+'film/film.blend'); print('VEG_OK')
