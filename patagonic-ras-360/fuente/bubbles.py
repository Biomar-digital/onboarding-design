# Aeration bubble plumes as a Geometry Nodes system: diffusers on the floor, bubbles rising in a
# snaking column that widens upward. Everything is periodic over LOOP seconds (integer cycles), so the
# 90 s loop is seamless. Small bubbles rise straight and slow, big ones faster, flattened and spiralling.
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
                  ('T0','NodeSocketFloat',0.0),('Size Min','NodeSocketFloat',0.002),('Size Max','NodeSocketFloat',0.007)):
        _io(ng,n,t,v)
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
    # size: many small, few big
    rs=rnd(); size=M('ADD',gi.outputs['Size Min'],M('MULTIPLY',M('SUBTRACT',gi.outputs['Size Max'],gi.outputs['Size Min']),M('POWER',rs,3.0)))
    # rise: 1 cycle per loop for small bubbles (~0.19 m/s), 2 for big ones (~0.38 m/s)
    k=M('ADD',1.0,M('GREATER_THAN',rs,0.72))
    u=M('FRACT',M('ADD',rnd(),M('MULTIPLY',k,M('DIVIDE',t,LOOP))))
    z=M('MULTIPLY',u,gi.outputs['Height'])
    # column widens upward, roughly gaussian across
    sp=M('ADD',gi.outputs['Spread Bottom'],M('MULTIPLY',M('SUBTRACT',gi.outputs['Spread Top'],gi.outputs['Spread Bottom']),M('POWER',u,0.7)))
    rad=M('MULTIPLY',sp,M('POWER',rnd(),0.9)); ang=M('MULTIPLY',rnd(),2*math.pi)
    x=M('MULTIPLY',rad,M('COSINE',ang)); y=M('MULTIPLY',rad,M('SINE',ang))
    # spiral wobble, stronger for big bubbles; integer frequencies keep the loop seamless
    wn=rnd(55,125,True); ph=M('MULTIPLY',rnd(),2*math.pi)
    wa=M('ADD',0.002,M('MULTIPLY',size,3.0))
    arg=M('ADD',M('MULTIPLY',M('MULTIPLY',wn,w0),t),ph)
    x=M('ADD',x,M('MULTIPLY',wa,M('COSINE',arg))); y=M('ADD',y,M('MULTIPLY',wa,M('SINE',arg)))
    # the whole column snakes slowly with height (current), also loop-periodic
    sarg=M('ADD',M('MULTIPLY',z,0.45),M('MULTIPLY',3*w0,t))
    sway=M('MULTIPLY',gi.outputs['Sway'],M('POWER',u,0.8))
    x=M('ADD',x,M('MULTIPLY',sway,M('SINE',sarg))); y=M('ADD',y,M('MULTIPLY',M('MULTIPLY',sway,0.6),M('COSINE',M('ADD',sarg,1.3))))
    cmb=N.new('ShaderNodeCombineXYZ'); Lk.new(x,cmb.inputs[0]); Lk.new(y,cmb.inputs[1]); Lk.new(z,cmb.inputs[2])
    pts=N.new('GeometryNodePoints'); Lk.new(gi.outputs['Count'],pts.inputs['Count']); Lk.new(cmb.outputs[0],pts.inputs['Position'])
    sph=N.new('GeometryNodeMeshUVSphere'); sph.inputs['Segments'].default_value=14; sph.inputs['Rings'].default_value=7; sph.inputs['Radius'].default_value=1.0
    sm=N.new('GeometryNodeSetShadeSmooth'); Lk.new(sph.outputs['Mesh'],sm.inputs['Geometry'])
    smat=N.new('GeometryNodeSetMaterial'); smat.inputs['Material'].default_value=mat; Lk.new(sm.outputs[0],smat.inputs['Geometry'])
    # big bubbles flatten (oblate) and tilt with the wobble
    flat=M('SUBTRACT',1.0,M('MULTIPLY',0.4,M('MINIMUM',1.0,M('MAXIMUM',0.0,M('DIVIDE',M('SUBTRACT',size,0.0025),0.004)))))
    scl=N.new('ShaderNodeCombineXYZ'); Lk.new(size,scl.inputs[0]); Lk.new(size,scl.inputs[1]); Lk.new(M('MULTIPLY',size,flat),scl.inputs[2])
    rot=N.new('ShaderNodeCombineXYZ'); Lk.new(M('MULTIPLY',0.35,M('SINE',arg)),rot.inputs[0]); Lk.new(M('MULTIPLY',0.35,M('COSINE',arg)),rot.inputs[1])
    iop=N.new('GeometryNodeInstanceOnPoints'); Lk.new(pts.outputs[0],iop.inputs['Points']); Lk.new(smat.outputs[0],iop.inputs['Instance'])
    Lk.new(scl.outputs[0],iop.inputs['Scale']); Lk.new(rot.outputs[0],iop.inputs['Rotation'])
    Lk.new(iop.outputs[0],go.inputs[0])
    return ng

def material():
    # air in water: almost clear in the centre, silvery rim (total internal reflection) and a sharp highlight
    m=bpy.data.materials.new('bubble'); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links
    N.remove(N['Principled BSDF']); out=N['Material Output']
    lw=N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value=0.35
    rim=N.new('ShaderNodeMath'); rim.operation='POWER'; L.new(lw.outputs['Facing'],rim.inputs[0]); rim.inputs[1].default_value=1.6
    tr=N.new('ShaderNodeBsdfTransparent')
    gl=N.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value=0.03; gl.inputs['Color'].default_value=(1,1,1,1)
    em=N.new('ShaderNodeEmission'); em.inputs['Color'].default_value=(0.75,0.9,1.0,1); em.inputs['Strength'].default_value=1.6
    a1=N.new('ShaderNodeAddShader'); L.new(gl.outputs[0],a1.inputs[0]); L.new(em.outputs[0],a1.inputs[1])
    mx=N.new('ShaderNodeMixShader'); L.new(rim.outputs[0],mx.inputs['Fac']); L.new(tr.outputs[0],mx.inputs[1]); L.new(a1.outputs[0],mx.inputs[2])
    L.new(mx.outputs[0],out.inputs['Surface'])
    return m

def plume(sc,ng,loc,height,count,seed,T0,spread_top=0.9,sway=0.25,size_max=0.007):
    me=bpy.data.meshes.new('plume'); ob=bpy.data.objects.new('BubblePlume',me); sc.collection.objects.link(ob)
    ob.location=loc; ob.visible_shadow=False
    md=ob.modifiers.new('bubbles','NODES'); md.node_group=ng
    vals={'Count':count,'Seed':seed,'Height':height,'Spread Top':spread_top,'Sway':sway,'T0':T0,'Size Max':size_max}
    for it in ng.interface.items_tree:
        if it.in_out=='INPUT' and it.name in vals: md[it.identifier]=vals[it.name]
    return ob
