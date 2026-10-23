# Aeration bubble plumes as a Geometry Nodes system: diffusers on the floor, bubbles rising in a
# snaking column that widens upward and leans with the tank current. Periodic over LOOP seconds, so the
# 90 s loop is seamless. Sizes, shapes and zigzag follow real bubble physics (see comments).
import bpy, math
LOOP=90.0

def _io(ng,name,typ,val=None,out=False):
    s=ng.interface.new_socket(name,in_out='OUTPUT' if out else 'INPUT',socket_type=typ)
    if val is not None: s.default_value=val
    return s

def group(mat):
    ng=bpy.data.node_groups.new('BubblePlume','GeometryNodeTree')
    _io(ng,'Geometry','NodeSocketGeometry',out=True)
    for n,t,v in (('Count','NodeSocketInt',1200),('Seed','NodeSocketInt',0),('Height','NodeSocketFloat',17.0),
                  ('Spread Bottom','NodeSocketFloat',0.05),('Spread Top','NodeSocketFloat',0.9),('Sway','NodeSocketFloat',0.25),
                  ('T0','NodeSocketFloat',0.0),('Size Min','NodeSocketFloat',0.0005),('Size Max','NodeSocketFloat',0.0015)):
        _io(ng,n,t,v)
    _io(ng,'Current','NodeSocketVector',(0.0,0.0,0.0))
    N=ng.nodes; Lk=ng.links
    gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    def sock(x): return x
    def link(a,b):
        if isinstance(a,(int,float)): b.default_value=a
        else: Lk.new(a,b)
    def M(op,a,b=None,c=None):
        n=N.new('ShaderNodeMath'); n.operation=op
        link(a,n.inputs[0])
        if b is not None: link(b,n.inputs[1])
        if c is not None: link(c,n.inputs[2])
        return n.outputs[0]
    idx=N.new('GeometryNodeInputIndex').outputs[0]
    k_=[0]
    def rnd(lo=0.0,hi=1.0,integer=False):
        n=N.new('FunctionNodeRandomValue'); n.data_type='INT' if integer else 'FLOAT'
        ins={s.identifier:s for s in n.inputs}
        if integer: ins['Min_002'].default_value=lo; ins['Max_002'].default_value=hi
        else: ins['Min_001'].default_value=lo; ins['Max_001'].default_value=hi
        Lk.new(idx,ins['ID']); k_[0]+=1
        Lk.new(M('ADD',gi.outputs['Seed'],k_[0]*7919),ins['Seed'])
        outs={s.identifier:s for s in n.outputs}
        return outs['Value_002' if integer else 'Value_001']
    st=N.new('GeometryNodeInputSceneTime')
    t=M('ADD',M('DIVIDE',M('SUBTRACT',st.outputs['Frame'],1.0),24.0),gi.outputs['T0'])     # seconds, same clock as the fish
    w0=2*math.pi/LOOP
    # size (radius): fine-bubble aeration, mostly 1-3 mm diameter, a few coarse ones
    rs=rnd(); size=M('ADD',gi.outputs['Size Min'],M('MULTIPLY',M('SUBTRACT',gi.outputs['Size Max'],gi.outputs['Size Min']),M('POWER',rs,2.5)))
    # rise ~0.19 m/s for all (terminal speed of 1-6 mm bubbles in aquaculture water is ~0.15-0.25 m/s); 1 cycle per loop
    rise=M('DIVIDE',gi.outputs['Height'],LOOP)
    u=M('FRACT',M('ADD',rnd(),M('DIVIDE',t,LOOP)))
    z=M('MULTIPLY',u,gi.outputs['Height'])
    # column widens upward, roughly gaussian across
    sp=M('ADD',gi.outputs['Spread Bottom'],M('MULTIPLY',M('SUBTRACT',gi.outputs['Spread Top'],gi.outputs['Spread Bottom']),M('POWER',u,0.7)))
    rad=M('MULTIPLY',sp,M('POWER',rnd(),0.9)); ang=M('MULTIPLY',rnd(),2*math.pi)
    x=M('MULTIPLY',rad,M('COSINE',ang)); y=M('MULTIPLY',rad,M('SINE',ang))
    # path instability: above ~1.5 mm diameter bubbles zigzag/spiral a few times per second, amplitude ~ their size
    wn=rnd(180,330,True); ph=M('MULTIPLY',rnd(),2*math.pi)
    big=M('MINIMUM',1.0,M('MAXIMUM',0.0,M('DIVIDE',M('SUBTRACT',size,0.0007),0.0008)))
    wa=M('MULTIPLY',size,M('ADD',0.15,M('MULTIPLY',1.6,big)))
    arg=M('ADD',M('MULTIPLY',M('MULTIPLY',wn,w0),t),ph)
    x=M('ADD',x,M('MULTIPLY',wa,M('COSINE',arg))); y=M('ADD',y,M('MULTIPLY',wa,M('SINE',arg)))
    # the column snakes slowly (turbulence), loop-periodic
    sarg=M('ADD',M('MULTIPLY',z,0.45),M('MULTIPLY',3*w0,t))
    sway=M('MULTIPLY',gi.outputs['Sway'],M('POWER',u,0.8))
    x=M('ADD',x,M('MULTIPLY',sway,M('SINE',sarg))); y=M('ADD',y,M('MULTIPLY',M('MULTIPLY',sway,0.6),M('COSINE',M('ADD',sarg,1.3))))
    # tank current: a bubble that has risen z metres has been carried current*z/rise downstream -> leaning column
    cur=N.new('ShaderNodeSeparateXYZ'); Lk.new(gi.outputs['Current'],cur.inputs[0]); tr=M('DIVIDE',z,rise)
    x=M('ADD',x,M('MULTIPLY',cur.outputs[0],tr)); y=M('ADD',y,M('MULTIPLY',cur.outputs[1],tr))
    cmb=N.new('ShaderNodeCombineXYZ'); Lk.new(x,cmb.inputs[0]); Lk.new(y,cmb.inputs[1]); Lk.new(z,cmb.inputs[2])
    pts=N.new('GeometryNodePoints'); Lk.new(gi.outputs['Count'],pts.inputs['Count']); Lk.new(cmb.outputs[0],pts.inputs['Position'])
    sph=N.new('GeometryNodeMeshUVSphere'); sph.inputs['Segments'].default_value=14; sph.inputs['Rings'].default_value=7; sph.inputs['Radius'].default_value=1.0
    sm=N.new('GeometryNodeSetShadeSmooth'); Lk.new(sph.outputs['Mesh'],sm.inputs['Geometry'])
    smat=N.new('GeometryNodeSetMaterial'); smat.inputs['Material'].default_value=mat; Lk.new(sm.outputs[0],smat.inputs['Geometry'])
    # shape from the Eotvos number (Wellek): aspect E = 1 + 0.163 Eo^0.757, Eo = (rho g d^2)/sigma
    # 2 mm -> 1.10 (almost a sphere), 4 mm -> 1.29, 6 mm -> 1.54; volume preserved
    d=M('MULTIPLY',size,2.0); eo=M('MULTIPLY',M('MULTIPLY',d,d),1000*9.81/0.072)
    E=M('ADD',1.0,M('MULTIPLY',0.163,M('POWER',eo,0.757)))
    sxy=M('MULTIPLY',size,M('POWER',E,1/3)); sz=M('DIVIDE',size,M('POWER',E,2/3))
    scl=N.new('ShaderNodeCombineXYZ'); Lk.new(sxy,scl.inputs[0]); Lk.new(sxy,scl.inputs[1]); Lk.new(sz,scl.inputs[2])
    tilt=M('MULTIPLY',0.3,big)
    rot=N.new('ShaderNodeCombineXYZ'); Lk.new(M('MULTIPLY',tilt,M('SINE',arg)),rot.inputs[0]); Lk.new(M('MULTIPLY',tilt,M('COSINE',arg)),rot.inputs[1])
    iop=N.new('GeometryNodeInstanceOnPoints'); Lk.new(pts.outputs[0],iop.inputs['Points']); Lk.new(smat.outputs[0],iop.inputs['Instance'])
    Lk.new(scl.outputs[0],iop.inputs['Scale']); Lk.new(rot.outputs[0],iop.inputs['Rotation'])
    Lk.new(iop.outputs[0],go.inputs[0])
    return ng

def material():
    # physically an air bubble in water is a glass sphere with IOR 1/1.33: the centre refracts (a small
    # minified image of the bright water above), the rim goes to total internal reflection (silver).
    # Needs enough transmission/glossy bounces in the render settings.
    m=bpy.data.materials.new('bubble'); m.use_nodes=True; nt=m.node_tree; N=nt.nodes
    N.remove(N['Principled BSDF'])
    g=N.new('ShaderNodeBsdfGlass'); g.inputs['IOR'].default_value=1/1.33; g.inputs['Roughness'].default_value=0.035     # tiny roughness lets the sun be sampled: glints inside light shafts
    nt.links.new(g.outputs[0],N['Material Output'].inputs['Surface'])
    return m

def plume(sc,ng,loc,height,count,seed,T0,spread_top=0.9,sway=0.25,size_max=0.0015,size_min=0.0005,current=(0,0,0)):
    me=bpy.data.meshes.new('plume'); ob=bpy.data.objects.new('BubblePlume',me); sc.collection.objects.link(ob)
    ob.location=loc; ob.visible_shadow=False
    md=ob.modifiers.new('bubbles','NODES'); md.node_group=ng
    vals={'Count':count,'Seed':seed,'Height':height,'Spread Top':spread_top,'Sway':sway,'T0':T0,'Size Max':size_max,'Size Min':size_min}
    cur=[it.identifier for it in ng.interface.items_tree if it.in_out=='INPUT' and it.name=='Current'][0]
    for it in ng.interface.items_tree:
        if it.in_out=='INPUT' and it.name in vals: md[it.identifier]=vals[it.name]
    md[cur]=list(current)
    return ob

def snow_group(flakes_coll):
    # marine snow / organic flocs carried by the tank current: points in a box that slide along the current
    # and wrap around; box length = current*LOOP/n, so after 90 s every flake is exactly back in place
    ng=bpy.data.node_groups.new('Snow','GeometryNodeTree')
    _io(ng,'Geometry','NodeSocketGeometry',out=True)
    for n,t,v in (('Count','NodeSocketInt',3000),('Seed','NodeSocketInt',0),('Length','NodeSocketFloat',12.6),('Laps','NodeSocketInt',2),
                  ('Depth','NodeSocketFloat',9.0),('Height','NodeSocketFloat',8.0),('T0','NodeSocketFloat',0.0)):
        _io(ng,n,t,v)
    N=ng.nodes; Lk=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    def M(op,a,b=None):
        n=N.new('ShaderNodeMath'); n.operation=op
        for s,x in ((n.inputs[0],a),(n.inputs[1],b)):
            if x is None: continue
            if isinstance(x,(int,float)): s.default_value=x
            else: Lk.new(x,s)
        return n.outputs[0]
    idx=N.new('GeometryNodeInputIndex').outputs[0]; kk=[0]
    def rnd(lo=0.0,hi=1.0,integer=False):
        n=N.new('FunctionNodeRandomValue'); n.data_type='INT' if integer else 'FLOAT'; ins={s.identifier:s for s in n.inputs}
        ins['Min_002' if integer else 'Min_001'].default_value=lo; ins['Max_002' if integer else 'Max_001'].default_value=hi
        Lk.new(idx,ins['ID']); kk[0]+=1; Lk.new(M('ADD',gi.outputs['Seed'],kk[0]*104729),ins['Seed'])
        return {s.identifier:s for s in n.outputs}['Value_002' if integer else 'Value_001']
    st=N.new('GeometryNodeInputSceneTime'); t=M('ADD',M('DIVIDE',M('SUBTRACT',st.outputs['Frame'],1.0),24.0),gi.outputs['T0'])
    w0=2*math.pi/LOOP
    # local frame of the object: x = downstream, y = depth (away from the screen), z = up
    x=M('MULTIPLY',M('SUBTRACT',M('FRACT',M('ADD',rnd(),M('DIVIDE',M('MULTIPLY',t,gi.outputs['Laps']),LOOP))),0.5),gi.outputs['Length'])
    y=M('MULTIPLY',M('POWER',rnd(),0.8),gi.outputs['Depth'])
    # slow turbulent wander, loop-periodic (integer frequencies)
    ph=M('MULTIPLY',rnd(),6.283); fq=rnd(4,11,True); a=M('MULTIPLY',rnd(),0.12)
    zz=M('ADD',M('MULTIPLY',M('SUBTRACT',rnd(),0.5),gi.outputs['Height']),M('MULTIPLY',a,M('SINE',M('ADD',M('MULTIPLY',M('MULTIPLY',fq,w0),t),ph))))
    y=M('ADD',y,M('MULTIPLY',a,M('COSINE',M('ADD',M('MULTIPLY',M('MULTIPLY',fq,w0),t),ph))))
    cmb=N.new('ShaderNodeCombineXYZ'); Lk.new(x,cmb.inputs[0]); Lk.new(y,cmb.inputs[1]); Lk.new(zz,cmb.inputs[2])
    pts=N.new('GeometryNodePoints'); Lk.new(gi.outputs['Count'],pts.inputs['Count']); Lk.new(cmb.outputs[0],pts.inputs['Position'])
    ci=N.new('GeometryNodeCollectionInfo'); ci.inputs['Collection'].default_value=flakes_coll; ci.inputs['Separate Children'].default_value=True; ci.inputs['Reset Children'].default_value=True
    iop=N.new('GeometryNodeInstanceOnPoints'); Lk.new(pts.outputs[0],iop.inputs['Points']); Lk.new(ci.outputs[0],iop.inputs['Instance'])
    iop.inputs['Pick Instance'].default_value=True; Lk.new(rnd(0,15,True),iop.inputs['Instance Index'])
    # size: mostly fine specks (~2 mm), a few flocs (~1 cm); slow tumble
    rs=rnd(); sz=M('ADD',0.0009,M('MULTIPLY',0.007,M('POWER',rs,6.0)))
    sv=N.new('ShaderNodeCombineXYZ')
    for i,f in enumerate((rnd(0.5,1.5),rnd(0.5,1.5),rnd(0.8,1.0))): Lk.new(M('MULTIPLY',sz,f),sv.inputs[i])
    rot=N.new('ShaderNodeCombineXYZ')
    for i in range(3): Lk.new(M('ADD',M('MULTIPLY',rnd(),6.283),M('MULTIPLY',M('MULTIPLY',rnd(1,3,True),w0),t)),rot.inputs[i])
    Lk.new(sv.outputs[0],iop.inputs['Scale']); Lk.new(rot.outputs[0],iop.inputs['Rotation'])
    Lk.new(iop.outputs[0],go.inputs[0])
    return ng

def snow(sc,ng,loc,rot_z,count,seed,T0,length,laps,depth,height):
    me=bpy.data.meshes.new('snow'); ob=bpy.data.objects.new('Snow',me); sc.collection.objects.link(ob)
    ob.location=loc; ob.rotation_euler=(0,0,rot_z); ob.visible_shadow=False
    md=ob.modifiers.new('snow','NODES'); md.node_group=ng
    vals={'Count':count,'Seed':seed,'T0':T0,'Length':length,'Laps':laps,'Depth':depth,'Height':height}
    for it in ng.interface.items_tree:
        if it.in_out=='INPUT' and it.name in vals: md[it.identifier]=vals[it.name]
    return ob
