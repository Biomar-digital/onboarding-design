# Fish eggs under a brightfield microscope (look matched to the client's reference photo).
# Eggs sit in water, so every IOR here is RELATIVE to water: tissue barely bends light, the oil drop (n~1.47) does.
# Koehler-style illumination (light only from a narrow cone below) + telecentric (ortho) camera: rays bent more than a few
# degrees see black -> thin dark outlines, black oil drop with a bright centre, exactly how brightfield images look.
# blender -b --factory-startup -P eggs.py -- OUT.png [samples] [width]
import bpy, bmesh, math, random, sys, mathutils
args=sys.argv[sys.argv.index('--')+1:]; OUT=args[0]; SPP=int(args[1]) if len(args)>1 else 96; RW=int(args[2]) if len(args)>2 else 1600
bpy.ops.wm.read_factory_settings(use_empty=True); sc=bpy.context.scene; random.seed(7)
def sphere(name,r,loc,seg=48):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); bmesh.ops.create_uvsphere(bm,u_segments=seg,v_segments=seg//2,radius=r); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    o=bpy.data.objects.new(name,me); sc.collection.objects.link(o); o.location=loc; return o
def mat(name):
    m=bpy.data.materials.new(name); m.use_nodes=True; return m,m.node_tree.nodes,m.node_tree.links
def glass(b,ior,rough,col=(1,1,1,1)):
    b.inputs['Transmission Weight'].default_value=1; b.inputs['IOR'].default_value=ior; b.inputs['Roughness'].default_value=rough; b.inputs['Base Color'].default_value=col
# ---- chorion: thin transparent shell (solidified sphere) -> the crisp double line at the egg edge
chor,N,Lk=mat('chorion'); glass(N['Principled BSDF'],1.07,0.02,(0.97,1.0,0.98,1))
# ---- yolk: almost index-matched, fine dark stipple + soft cloudy shading
yolk,N,Lk=mat('yolk'); b=N['Principled BSDF']; glass(b,1.008,0.1,(0.98,0.97,0.97,1))
vo=N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value=60; vo.inputs['Randomness'].default_value=1.0
# granular ring on the cap facing the lens (the 'flower' seen in the photo): denser stipple in a ring around the yolk top
ytc=N.new('ShaderNodeTexCoord'); ysp=N.new('ShaderNodeSeparateXYZ'); Lk.new(ytc.outputs['Object'],ysp.inputs[0])
def YM(op,a,bb=None):
    n=N.new('ShaderNodeMath'); n.operation=op
    for i,x in enumerate((a,bb)):
        if x is None: continue
        if isinstance(x,(int,float)): n.inputs[i].default_value=x
        else: Lk.new(x,n.inputs[i])
    return n.outputs[0]
dxy=YM('SQRT',YM('ADD',YM('MULTIPLY',ysp.outputs['X'],ysp.outputs['X']),YM('MULTIPLY',ysp.outputs['Y'],ysp.outputs['Y'])))
rd=YM('SUBTRACT',dxy,0.24); ring=YM('MULTIPLY',YM('EXPONENT',YM('MULTIPLY',YM('MULTIPLY',rd,rd),-90)),YM('GREATER_THAN',ysp.outputs['Z'],0.3))
sk=N.new('ShaderNodeMapRange'); Lk.new(vo.outputs['Distance'],sk.inputs[0]); sk.inputs[1].default_value=0.14; Lk.new(YM('ADD',YM('MULTIPLY',ring,0.3),0.2),sk.inputs[2]); sk.inputs[3].default_value=0.85; sk.inputs[4].default_value=0.0
dk=N.new('ShaderNodeBsdfTransparent'); dk.inputs['Color'].default_value=(0.3,0.27,0.28,1); mx=N.new('ShaderNodeMixShader')
Lk.new(sk.outputs[0],mx.inputs[0]); Lk.new(b.outputs[0],mx.inputs[1]); Lk.new(dk.outputs[0],mx.inputs[2]); Lk.new(mx.outputs[0],N['Material Output'].inputs['Surface'])
va=N.new('ShaderNodeVolumeAbsorption'); va.inputs['Color'].default_value=(0.8,0.78,0.78,1)
nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=3.5; nz.inputs['Detail'].default_value=3
gr=N.new('ShaderNodeMapRange'); Lk.new(nz.outputs['Fac'],gr.inputs[0]); gr.inputs[1].default_value=0.35; gr.inputs[2].default_value=0.65; gr.inputs[3].default_value=0.1; gr.inputs[4].default_value=2.2
Lk.new(gr.outputs[0],va.inputs['Density']); Lk.new(va.outputs[0],N['Material Output'].inputs['Volume'])
# ---- oil globule: strong lens
oil,N,Lk=mat('oil'); glass(N['Principled BSDF'],1.4,0.0,(0.97,0.97,0.93,1))
# ---- embryo tissue: translucent, chevron myomeres along the body
emb,N,Lk=mat('embryo'); b=N['Principled BSDF']; glass(b,1.05,0.2,(0.96,0.95,0.94,1))
tc=N.new('ShaderNodeTexCoord'); sep=N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['UV'],sep.inputs[0])
def M(op,a,bb):
    n=N.new('ShaderNodeMath'); n.operation=op
    for i,x in enumerate((a,bb)):
        if isinstance(x,(int,float)): n.inputs[i].default_value=x
        else: Lk.new(x,n.inputs[i])
    return n.outputs[0]
chev=M('ADD',sep.outputs['X'],M('MULTIPLY',M('ABSOLUTE',M('SUBTRACT',M('FRACT',M('MULTIPLY',sep.outputs['Y'],2.0),0),0.5),0),0.05))   # V-shaped somites
som=M('SINE',M('MULTIPLY',chev,2*math.pi*26),0)
noc=M('MULTIPLY',M('POWER',M('ABSOLUTE',M('COSINE',M('MULTIPLY',sep.outputs['Y'],2*math.pi),0),0),12.0),1.5)   # notochord ridge on top
tn=N.new('ShaderNodeTexNoise'); tn.inputs['Scale'].default_value=60; tn.inputs['Detail'].default_value=4
hgt=M('ADD',M('ADD',M('MULTIPLY',som,0.6),noc),M('MULTIPLY',tn.outputs['Fac'],0.8))   # cellular texture
# transmitted tint: thin darker myomere boundaries + notochord band + cellular mottling (what makes the body read as tissue)
stripe=M('POWER',M('MULTIPLY',M('ADD',som,1.0),0.5),8.0)
band=M('MULTIPLY',M('POWER',M('ABSOLUTE',M('COSINE',M('MULTIPLY',sep.outputs['Y'],2*math.pi),0),0),30.0),0.6)
dark=M('MINIMUM',M('ADD',M('ADD',M('MULTIPLY',stripe,0.45),band),M('MULTIPLY',tn.outputs['Fac'],0.35)),0.8)
cr=N.new('ShaderNodeMix'); cr.data_type='RGBA'; Lk.new(dark,cr.inputs['Factor']); cr.inputs[6].default_value=(0.97,0.95,0.94,1); cr.inputs[7].default_value=(0.6,0.57,0.57,1)
Lk.new(cr.outputs[2],b.inputs['Base Color'])
bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.2; Lk.new(hgt,bp.inputs['Height']); Lk.new(bp.outputs['Normal'],b.inputs['Normal'])
ev=N.new('ShaderNodeVolumeAbsorption'); ev.inputs['Color'].default_value=(0.8,0.76,0.72,1); ev.inputs['Density'].default_value=0.45; Lk.new(ev.outputs[0],N['Material Output'].inputs['Volume'])
eye,N,Lk=mat('eye'); glass(N['Principled BSDF'],1.015,0.3,(0.9,0.88,0.86,1))
deep,N,Lk=mat('deep'); N.remove(N['Principled BSDF']); t_=N.new('ShaderNodeBsdfTransparent'); Lk.new(t_.outputs[0],N['Material Output'].inputs['Surface'])
da=N.new('ShaderNodeVolumeAbsorption'); da.inputs['Color'].default_value=(0.55,0.52,0.55,1); dn=N.new('ShaderNodeTexNoise'); dn.inputs['Scale'].default_value=6
dr=N.new('ShaderNodeMapRange'); Lk.new(dn.outputs['Fac'],dr.inputs[0]); dr.inputs[1].default_value=0.35; dr.inputs[2].default_value=0.7; dr.inputs[3].default_value=0.0; dr.inputs[4].default_value=2.5
Lk.new(dr.outputs[0],da.inputs['Density']); Lk.new(da.outputs[0],N['Material Output'].inputs['Volume'])
# ---- one egg
def egg(c,rad):
    o=sphere('chorion',rad,c,96); o.data.materials.append(chor)
    s=o.modifiers.new('shell','SOLIDIFY'); s.thickness=0.035*rad; s.offset=-1; s.use_even_offset=True
    R=(mathutils.Matrix.Rotation(random.uniform(0,6.28),3,'Z')@mathutils.Matrix.Rotation(random.uniform(1.45,1.57) if random.random()<0.22 else random.uniform(0.25,1.0),3,'X'))   # embryo lies across the face
    yc=mathutils.Vector(c)+R@mathutils.Vector((0,0,-0.06*rad)); sphere('yolk',rad*0.9,yc,64).data.materials.append(yolk)
    cl=sphere('deep',rad*random.uniform(0.3,0.42),mathutils.Vector(c)+mathutils.Vector((random.uniform(-0.25,0.25)*rad,random.uniform(-0.25,0.25)*rad,-0.45*rad)),32); cl.data.materials.append(deep)
    oc=mathutils.Vector(c)+mathutils.Vector((random.uniform(-0.45,0.45)*rad,random.uniform(-0.45,0.45)*rad,0.35*rad))
    sphere('oil',rad*random.uniform(0.21,0.25),oc,48).data.materials.append(oil)
    # embryo: arc lying on the yolk, wide trunk, tapering tail
    cu=bpy.data.curves.new('emb','CURVE'); cu.dimensions='3D'; cu.bevel_depth=0.15*rad; cu.bevel_resolution=8
    cu.use_fill_caps=True
    sp=cu.splines.new('POLY'); n=60; span=random.uniform(2.0,3.4); a0=math.pi/2-span/2+random.uniform(-0.4,0.4); rr=rad*0.84
    sp.points.add(n-1)
    for i in range(n):
        u=i/(n-1); ang=a0+span*u; p=yc+R@mathutils.Vector((rr*math.cos(ang),rr*math.sin(ang),0.0))
        sp.points[i].co=(p.x,p.y,p.z,1); sp.points[i].radius=1.0 if u<0.62 else 1.0-0.85*((u-0.62)/0.38)**1.3
    eo=bpy.data.objects.new('embryo',cu); sc.collection.objects.link(eo); cu.materials.append(emb)
    # head: bulb at the front end with two optic cups
    tang=R@mathutils.Vector((-math.sin(a0),math.cos(a0),0))
    hp=yc+R@mathutils.Vector((rr*0.92*math.cos(a0),rr*0.92*math.sin(a0),0))-tang*0.05*rad
    h=sphere('head',0.22*rad,hp,40); h.data.materials.append(emb)
    h.rotation_mode='QUATERNION'; h.rotation_quaternion=tang.to_track_quat('X','Z'); h.scale=(1.1,1.0,0.95)
    nrm=(hp-mathutils.Vector(c)).normalized(); side=tang.cross(nrm).normalized()
    for sgn in (-1,1): sphere('eye',0.05*rad,hp-tang*0.06*rad+side*sgn*0.1*rad,24).data.materials.append(eye)
# tight cluster like the photo: touching hex packing, an empty corner (top right), a few eggs missing
rad=1.0; L=random.Random(3)
for row in range(-3,4):
    for col in range(-4,5):
        x=col*2.04*rad+(1.02*rad if row%2 else 0)+L.uniform(-0.05,0.05); y=row*1.78*rad+L.uniform(-0.05,0.05)
        if x*0.55+y>2.6+L.uniform(-0.6,0.6): continue
        egg((x,y,random.uniform(-0.1,0.1)),rad*random.uniform(0.97,1.02))
# ---- illumination: world lights only from a narrow cone below
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; wn=w.node_tree; wb=wn.nodes['Background']; wb.inputs['Color'].default_value=(0.84,0.83,0.87,1)
wt=wn.nodes.new('ShaderNodeTexCoord'); wz=wn.nodes.new('ShaderNodeSeparateXYZ'); wn.links.new(wt.outputs['Generated'],wz.inputs[0])
wr=wn.nodes.new('ShaderNodeMapRange'); wn.links.new(wz.outputs['Z'],wr.inputs[0]); wr.inputs[1].default_value=-0.9945; wr.inputs[2].default_value=-0.9848
wr.inputs[3].default_value=1.0; wr.inputs[4].default_value=0.0; wr.clamp=True; wn.links.new(wr.outputs[0],wb.inputs[1])
# ---- microscope camera: telecentric, shallow focus
cd=bpy.data.cameras.new('cam'); cd.type='ORTHO'; cd.ortho_scale=7.6; cam=bpy.data.objects.new('cam',cd); sc.collection.objects.link(cam); cam.location=(-0.6,-0.4,24); sc.camera=cam
cd.dof.use_dof=True; cd.dof.focus_distance=24.0; cd.dof.aperture_fstop=1.3
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SPP; sc.cycles.use_denoising=True
sc.cycles.max_bounces=32; sc.cycles.transmission_bounces=32; sc.cycles.transparent_max_bounces=32; sc.cycles.volume_bounces=0
sc.render.resolution_x=RW; sc.render.resolution_y=int(RW*0.75)
sc.view_settings.view_transform='Standard'; sc.view_settings.look='None'
# compositor: slight chromatic fringe of the objective, gentle contrast
sc.use_nodes=True; ct=sc.node_tree; ct.nodes.clear(); rl=ct.nodes.new('CompositorNodeRLayers'); ld=ct.nodes.new('CompositorNodeLensdist'); ld.inputs['Dispersion'].default_value=0.01
bc=ct.nodes.new('CompositorNodeBrightContrast'); bc.inputs['Contrast'].default_value=0
co=ct.nodes.new('CompositorNodeComposite'); ct.links.new(rl.outputs['Image'],ld.inputs['Image']); ct.links.new(ld.outputs['Image'],bc.inputs['Image']); ct.links.new(bc.outputs['Image'],co.inputs['Image'])
sc.render.filepath=OUT; bpy.ops.render.render(write_still=True); print('DONE')
