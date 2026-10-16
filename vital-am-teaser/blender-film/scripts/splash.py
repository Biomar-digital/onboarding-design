# Feed hitting the water (shot s3): per-impact crown, Worthington jet and a few thrown droplets, an air cavity behind
# each pellet just under the surface. Impacts come from the previs: ring births (every pellet) and hero pellet crossings.
import json, math, random
from mathutils import Vector, Matrix
_IMP=None; _CROSS=None
G=-9.8; FPS=24.0
def _b(x,y,z): return Vector((x,-z,y))          # three.js (y up) -> blender (z up), same convention as the sun vector
def load(S):
    global _IMP,_CROSS
    if _IMP is not None: return _IMP,_CROSS
    seen={}; prev={}; cross={}
    with open(S+'bt/dump.jsonl') as fh:
        for line in fh:
            d=json.loads(line); F=d['F']
            if F<245: continue
            if F>310: break
            for r in d['inst'].get('ring',[]):
                k=(round(r[12],3),round(r[14],3))
                if k not in seen: seen[k]=(F-1.0,_b(r[12],0.0,r[14]))
            for j,e in enumerate(d['inst']['hi']):
                y=e[13]
                if j in prev and prev[j][1]>0.0>=y and j not in cross:
                    F0,y0,x0,z0=prev[j]; t=y0/(y0-y)
                    cross[j]=(F0+t*(F-F0),_b(x0+(e[12]-x0)*t,0.0,z0+(e[14]-z0)*t))
                prev[j]=(F,y,e[12],e[14])
    _IMP=sorted(seen.values(),key=lambda v:v[0]); _CROSS=cross
    return _IMP,_CROSS
def splash(F,cam_pos,S,nmax=70):
    """matrices for drops (jet + droplets) and crowns at frame F"""
    imp,_=load(S); drops=[]; crowns=[]
    live=[(t0,c) for t0,c in imp if 0.0<=F-t0<16.0]
    live.sort(key=lambda v:(v[1]-cam_pos).length)
    for n,(t0,c) in enumerate(live[:nmax]):
        a=F-t0; rr=random.Random(int(c.x*1e4)*31+int(c.y*1e4)); s=rr.uniform(0.8,1.2)
        if a<4.0:   # crown: a thin wall that rises and collapses
            h=0.0019*s*math.sin(math.pi*a/4.0); R=(0.0014+0.0009*a)*s
            if h>0.0004:
                crowns.append(Matrix.Translation(c)@Matrix.Diagonal((R,R,h,1)))
                for q in range(9):   # beads on the rim, flung slightly outward as the crown opens
                    ang=2*math.pi*q/9+rr.uniform(-0.25,0.25); rq=R*1.05*(1+0.25*a/4.0)
                    rb=0.00025*rr.uniform(0.7,1.3)*s
                    drops.append(Matrix.Translation(c+Vector((math.cos(ang)*rq,math.sin(ang)*rq,h*1.02+0.0006*a)))@Matrix.Diagonal((rb,rb,rb*1.2,1)))
        if 2.5<=a<10.0:   # Worthington jet from the centre once the cavity closes
            u=(a-2.5)/7.5; H=0.011*s*math.sin(math.pi*u)
            if H>0.0006:
                w=0.0006*s*(1.0-0.4*u); drops.append(Matrix.Translation(c+Vector((0,0,H*0.5)))@Matrix.Diagonal((w,w,H*0.5,1)))
        for k in range(rr.randint(3,4)):   # droplets pinched off the jet tip, thrown up and out, falling back
            ak=4.0+k*0.8+rr.uniform(0,0.6); t=(a-ak)/FPS
            if t<0: continue
            ang=rr.uniform(0,2*math.pi); vh=rr.uniform(0.04,0.11); vz=rr.uniform(0.30,0.45)
            z=0.006*s+vz*t+0.5*G*t*t
            if z<=0.0: continue
            p=c+Vector((math.cos(ang)*vh*t,math.sin(ang)*vh*t,z)); r=rr.uniform(0.00045,0.0009)
            st=1.0+min(0.6,abs(vz+G*t)*0.8)   # slightly stretched along the motion
            drops.append(Matrix.Translation(p)@Matrix.Diagonal((r,r,r*st,1)))
    return drops,crowns
def cavity(F,pellets,S):
    """air pocket dragged behind each hero pellet for a few frames after it goes in; pellets: {j: blender pos}"""
    _,cross=load(S); out=[]
    for j,(tc,c0) in cross.items():
        a=F-tc
        if not (0.0<=a<6.0) or j not in pellets: continue
        p=pellets[j]; f=1.0-a/6.0; L=max(0.0005,min(-p.z,0.007*f)); r=0.0011*f+0.0003
        out.append(Matrix.Translation(p+Vector((0,0,L*0.5)))@Matrix.Diagonal((r,r,L*0.5+r,1)))
    return out
def cross_age(F,j,S):
    _,cross=load(S)
    return (F-cross[j][0]) if j in cross else None
# ---- ripples as a height field on the water surface material (instead of torus rings)
NSLOT=10
def build_ripples(mat):
    nt=mat.node_tree
    if 'RIP_T' in nt.nodes: return
    N=nt.nodes; L=nt.links
    def M(op,a=None,b=None,va=0.0,vb=0.0):
        n=N.new('ShaderNodeMath'); n.operation=op; n.inputs[0].default_value=va; n.inputs[1].default_value=vb
        if a is not None: L.new(a,n.inputs[0])
        if b is not None: L.new(b,n.inputs[1])
        return n.outputs[0]
    geo=N.new('ShaderNodeNewGeometry'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'],sep.inputs[0])
    tv=N.new('ShaderNodeValue'); tv.name='RIP_T'; T=tv.outputs[0]
    amp=N.new('ShaderNodeValue'); amp.name='RIP_A'; amp.outputs[0].default_value=1.0
    total=None
    for i in range(NSLOT):
        cx=N.new('ShaderNodeValue'); cx.name='RIP_X%d'%i; cy=N.new('ShaderNodeValue'); cy.name='RIP_Y%d'%i
        t0=N.new('ShaderNodeValue'); t0.name='RIP_T%d'%i; t0.outputs[0].default_value=1e5
        dx=M('SUBTRACT',sep.outputs[0],cx.outputs[0]); dy=M('SUBTRACT',sep.outputs[1],cy.outputs[0])
        r=M('SQRT',M('ADD',M('MULTIPLY',dx,dx),M('MULTIPLY',dy,dy)))
        age=M('DIVIDE',M('SUBTRACT',T,t0.outputs[0]),None,vb=24.0)           # seconds since impact
        on=M('GREATER_THAN',age,None,vb=0.0)
        front=M('MULTIPLY',age,None,vb=0.22)                                  # ripple packet speed ~22 cm/s
        sig=M('ADD',M('MULTIPLY',age,None,vb=0.05),None,vb=0.006)             # packet widens as it travels
        u=M('DIVIDE',M('SUBTRACT',r,front),sig)
        env=M('EXPONENT',M('MULTIPLY',M('MULTIPLY',u,u),None,vb=-1.0))
        dec=M('EXPONENT',M('MULTIPLY',age,None,vb=-2.2))                      # dies out in ~1 s
        wav=M('SINE',M('MULTIPLY',M('SUBTRACT',r,front),None,vb=2*math.pi/0.009))   # ~9 mm crests
        h=M('MULTIPLY',M('MULTIPLY',M('MULTIPLY',env,dec),wav),on)
        total=h if total is None else M('ADD',total,h)
    total=M('MULTIPLY',total,amp.outputs[0])
    bump=[n for n in N if n.type=='BUMP'][0]; src=bump.inputs['Height'].links[0].from_socket
    sc_=M('MULTIPLY',total,None,vb=1.0); N[-1].name='RIP_GAIN'
    L.new(M('ADD',src,sc_),bump.inputs['Height'])
def set_ripples(mat,F,cam_pos,S,gain):
    nt=mat.node_tree; N=nt.nodes
    if 'RIP_T' not in N: return
    imp,_=load(S); N['RIP_T'].outputs[0].default_value=F; N['RIP_GAIN'].inputs[1].default_value=gain
    live=[(t0,c) for t0,c in imp if 0.0<=F-t0<26.0]
    live.sort(key=lambda v:(v[1]-cam_pos).length)
    for i in range(NSLOT):
        if i<len(live) and gain>0:
            t0,c=live[i]; N['RIP_X%d'%i].outputs[0].default_value=c.x; N['RIP_Y%d'%i].outputs[0].default_value=c.y; N['RIP_T%d'%i].outputs[0].default_value=t0
        else: N['RIP_T%d'%i].outputs[0].default_value=1e5
def smooth_crown(me):
    """replace the 28-sided spiky crown with a smooth, thin flared water sheet with a soft scalloped rim"""
    if me.get('smooth_ok'): return
    import bmesh
    N=64; rows=[(0.45,0.0),(0.62,0.4),(0.84,0.75),(1.05,1.0)]
    vs=[]; fs=[]
    for k,(r,z) in enumerate(rows):
        for i in range(N):
            a=2*math.pi*i/N; sc=1.0+(0.035*math.sin(7*a)+0.02*math.sin(11*a+1.3))*(k/3.0)   # irregular scallops near the rim
            vs.append((r*sc*math.cos(a),r*sc*math.sin(a),z*(1.0+0.05*math.sin(9*a+0.7)*(k/3.0))))
    for k in range(len(rows)-1):
        for i in range(N):
            j=(i+1)%N; fs.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
    mats=list(me.materials); me.clear_geometry(); me.from_pydata(vs,[],fs)
    import bpy
    cm=bpy.data.materials.get('MAT_Crown')
    if cm is None:   # thin water sheet: mostly see-through, glints only at grazing angles
        cm=bpy.data.materials.new('MAT_Crown'); cm.use_nodes=True; nt=cm.node_tree; b=nt.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value=(0.92,0.97,0.95,1); b.inputs['Roughness'].default_value=0.04; b.inputs['IOR'].default_value=1.333
        b.inputs['Transmission Weight'].default_value=1.0
        tr=nt.nodes.new('ShaderNodeBsdfTransparent'); mx=nt.nodes.new('ShaderNodeMixShader'); lw=nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value=0.35
        rg=nt.nodes.new('ShaderNodeMath'); rg.operation='MULTIPLY'; rg.inputs[1].default_value=0.55
        nt.links.new(lw.outputs['Fresnel'],rg.inputs[0]); nt.links.new(rg.outputs[0],mx.inputs[0])
        nt.links.new(tr.outputs[0],mx.inputs[1]); nt.links.new(b.outputs[0],mx.inputs[2]); nt.links.new(mx.outputs[0],nt.nodes['Material Output'].inputs['Surface'])
    me.materials.clear(); me.materials.append(cm)
    for p in me.polygons: p.use_smooth=True
    me['smooth_ok']=1
