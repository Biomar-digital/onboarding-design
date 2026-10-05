# Anatomical Litopenaeus vannamei model (adult ~13 cm TL), articulated for animation.
# Local axes: +x anterior, +y left, +z dorsal. Root at the carapace/abdomen junction.
import bpy, bmesh, math
from mathutils import Vector, Matrix
D=bpy.data
def build_shrimp(prefix, col, origin=Vector((0,0,0)), rest_flex=-0.05):
    def mat(name,rgb,rough=0.35,trans=0.0):
        m=D.materials.get(name)
        if m: return m
        m=D.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough
        if 'Transmission Weight' in b.inputs: b.inputs['Transmission Weight'].default_value=trans
        return m
    M_body=mat('ANAT_Body',(0.80,0.83,0.84),0.28)
    M_red=mat('ANAT_Red',(0.62,0.26,0.20),0.4)
    M_eye=mat('ANAT_Eye',(0.02,0.02,0.025),0.15)
    M_fan=mat('ANAT_Fan',(0.66,0.50,0.46),0.35)
    def obj(name,bm,m,parent=None,loc=(0,0,0),smooth=True):
        me=D.meshes.new(prefix+name); bm.to_mesh(me); bm.free(); me.materials.append(m)
        if smooth:
            for p in me.polygons: p.use_smooth=True
        o=D.objects.new(prefix+name,me); col.objects.link(o)
        if parent: o.parent=parent
        o.location=loc; return o
    def section(x,w,ztop,zbot,n=20,carina=0.0,flat=0.0):
        pts=[]
        for k in range(n):
            a=2*math.pi*k/n; c,s=math.cos(a),math.sin(a)
            y=w/2*math.copysign(abs(s)**0.85,s)
            zc=(ztop+zbot)/2; hz=(ztop-zbot)/2
            z=zc+hz*math.copysign(abs(c)**0.9,c)
            if c<-0.7 and flat>0: z=max(z,zbot+flat)
            if c>0.9 and carina>0: z+=carina*(c-0.9)/0.1
            pts.append(Vector((x,y,z)))
        return pts
    def loft(secs,cap=True):
        bm=bmesh.new(); rings=[[bm.verts.new(p) for p in s] for s in secs]; n=len(secs[0])
        for a in range(len(rings)-1):
            for k in range(n): bm.faces.new((rings[a][k],rings[a][(k+1)%n],rings[a+1][(k+1)%n],rings[a+1][k]))
        if cap: bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces); return bm
    def tube(pts,r0,r1,n=6,bm=None):
        bm=bm or bmesh.new(); prev=None
        for i,p in enumerate(pts):
            t=i/(len(pts)-1); r=r0+(r1-r0)*t
            d=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
            u=d.orthogonal().normalized(); v=d.cross(u)
            ring=[bm.verts.new(p+r*(math.cos(2*math.pi*k/n)*u+math.sin(2*math.pi*k/n)*v)) for k in range(n)]
            if prev:
                for k in range(n): bm.faces.new((prev[k],prev[(k+1)%n],ring[(k+1)%n],ring[k]))
            prev=ring
        return bm
    def blade(outline,thick,bm=None,axis='y'):
        bm=bm or bmesh.new(); off=Vector((0,thick/2,0)) if axis=='y' else Vector((0,0,thick/2))
        top=[bm.verts.new(p+off) for p in outline]; bot=[bm.verts.new(p-off) for p in outline]
        bm.faces.new(top); bm.faces.new(bot[::-1]); n=len(outline)
        for k in range(n): bm.faces.new((top[k],bot[k],bot[(k+1)%n],top[(k+1)%n]))
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces); return bm
    def sphere(c,r,bm=None,sx=1,sy=1,sz=1):
        bm=bm or bmesh.new(); bmesh.ops.create_uvsphere(bm,u_segments=14,v_segments=10,radius=r,matrix=Matrix.Translation(c)@Matrix.Diagonal((sx,sy,sz,1))); return bm
    def bez(p0,p1,p2,n=10):
        return [p0*(1-t)**2+p1*2*t*(1-t)+p2*t*t for t in [i/(n-1) for i in range(n)]]
    root=D.objects.new(prefix+'Root',None); col.objects.link(root); root.location=origin; root.empty_display_size=0.02
    # cephalothorax: laterally compressed carapace with dorsal (adrostral) carina running into the rostrum
    xs=[0.0,0.005,0.012,0.020,0.027,0.033,0.037]
    W =[0.0118,0.0126,0.0128,0.0124,0.0112,0.0092,0.0066]
    T =[0.0098,0.0106,0.0112,0.0113,0.0110,0.0102,0.0088]
    B =[-0.0074,-0.0078,-0.0080,-0.0078,-0.0072,-0.0058,-0.0036]
    ceph_bm=loft([section(x,w,t,b,20,0.0007 if x>0.010 else 0.0,0.0012) for x,w,t,b in zip(xs,W,T,B)])
    # rostrum: 8 dorsal + 2 ventral teeth, reaching just past the antennular peduncle
    ol=[]; x0,x1=0.024,0.053
    for k in range(17):
        t=k/16; x=x0+(x1-x0)*t; zt=0.0118-0.0016*t
        tooth=0.0010*(1-0.5*t) if (k%2==1 and k<=15) else 0.0
        ol.append(Vector((x,0,zt+tooth)))
    ol.append(Vector((x1+0.0018,0,0.0098)))
    for k in range(16,-1,-1):
        t=k/16; x=x0+(x1-x0)*t; zb=0.0090-0.0001*t
        tooth=-0.0007 if k in (12,14) else 0.0
        if t<0.12: zb=0.0084
        ol.append(Vector((x,0,zb+tooth)))
    blade(ol,0.0011,ceph_bm)
    eye_bm=bmesh.new()
    for s in (-1,1):
        # eyes: short stalks at the front of the carapace, beside the rostral base
        tube([Vector((0.0355,0.0030*s,0.0042)),Vector((0.0385,0.0050*s,0.0046)),Vector((0.0400,0.0058*s,0.0048))],0.0013,0.0015,8,ceph_bm)
        sphere(Vector((0.0412,0.0063*s,0.0049)),0.0021,eye_bm)
        # antennules: peduncle + two short flagella
        tube([Vector((0.036,0.0020*s,0.0028)),Vector((0.043,0.0024*s,0.0034)),Vector((0.050,0.0026*s,0.0038))],0.0010,0.0007,6,ceph_bm)
        tube(bez(Vector((0.050,0.0026*s,0.0038)),Vector((0.060,0.0034*s,0.0066)),Vector((0.067,0.0050*s,0.0094)),8),0.00040,0.00014,5,ceph_bm)
        tube(bez(Vector((0.050,0.0024*s,0.0036)),Vector((0.059,0.0024*s,0.0030)),Vector((0.066,0.0040*s,0.0022)),8),0.00036,0.00014,5,ceph_bm)
        # antennal scale (scaphocerite): flat blade with lateral spine
        blade([Vector((0.0365,0.0056*s,0.0010)),Vector((0.046,0.0068*s,0.0016)),Vector((0.0545,0.0066*s,0.0020)),Vector((0.0560,0.0060*s,0.0019)),Vector((0.050,0.0048*s,0.0012)),Vector((0.040,0.0046*s,0.0006))],0.0005,ceph_bm,axis='z')
        # third maxillipeds held forward under the head
        tube([Vector((0.029,0.0024*s,-0.0066)),Vector((0.039,0.0034*s,-0.0090)),Vector((0.048,0.0036*s,-0.0094)),Vector((0.054,0.0032*s,-0.0084))],0.0006,0.0004,5,ceph_bm)
        # hepatic and antennal spines
        for c in (Vector((0.029,0.0058*s,0.0025)),Vector((0.0355,0.0040*s,0.0008))):
            sphere(c,0.0005,ceph_bm,sx=2.4)
    ceph=obj('Cephalothorax',ceph_bm,M_body,root)
    obj('Eyes',eye_bm,M_eye,ceph)
    # second antennae: long red flagella from below the eyes, arcing outward and back over the flanks
    for s,nm in ((1,'L'),(-1,'R')):
        bm=tube([Vector((0,0,0)),Vector((0.007,0.0018*s,0.0002))],0.0008,0.0006,6)
        path=bez(Vector((0.007,0.0018*s,0.0002)),Vector((0.026,0.016*s,0.006)),Vector((0.000,0.036*s,0.011)),10)+bez(Vector((0.000,0.036*s,0.011)),Vector((-0.050,0.060*s,0.013)),Vector((-0.150,0.078*s,0.006)),12)[1:]
        tube(path,0.00050,0.00010,5,bm)
        obj('Antenna_'+nm,bm,M_red,ceph,(0.0385,0.0046*s,-0.0004))
    # pereiopods: P1-P3 chelate (P3 longest), P4-P5 simple; slung under the body, tips on the substrate
    GROUND=-0.0180
    LEG=[(0.0270,True,0.006),(0.0222,True,0.004),(0.0172,True,0.0015),(0.0112,False,-0.002),(0.0058,False,-0.005)]
    for i,(x,chela,fwd) in enumerate(LEG):
        for s,nm in ((1,'L'),(-1,'R')):
            base=Vector((0,0,0)); knee=Vector((fwd*0.5,0.0050*s,-0.0010)); tip=Vector((fwd,(0.0042+0.0005*i)*s,GROUND+0.0072))
            pts=[base,knee*0.55+Vector((0,0.0006*s,0.0004)),knee,knee+(tip-knee)*0.5+Vector((0,0.0005*s,0)),tip]
            bm=tube(pts,0.00070,0.00038,6)
            if chela:
                d=(tip-knee).normalized()
                for off in (0.0006,-0.0006): tube([tip,tip+d*0.0024+Vector((0,0,off))],0.00030,0.00010,4,bm)
            obj('P%d_%s'%(i+1,nm),bm,M_body,ceph,(x,0.0030*s,-0.0070))
    # abdomen: six laterally compressed somites with pleura, arched dorsal profile, carina on 4-6
    SOM=[0.0094,0.0094,0.0094,0.0090,0.0086,0.0142]
    SW=[0.0112,0.0110,0.0104,0.0094,0.0082,0.0066,0.0046]
    ST=[0.0098,0.0104,0.0103,0.0097,0.0088,0.0074,0.0052]
    SB=[-0.0082,-0.0084,-0.0082,-0.0076,-0.0066,-0.0052,-0.0034]
    parent=ceph; abd=[]
    for i,Ls in enumerate(SOM):
        car=0.0008 if i>=3 else 0.0
        secs=[]
        for u in (0.0,0.2,0.45,0.7,0.9,1.0):
            sw=SW[i]+(SW[i+1]-SW[i])*u; st=ST[i]+(ST[i+1]-ST[i])*u; sb=SB[i]+(SB[i+1]-SB[i])*u
            bulge=0.0006*math.sin(math.pi*u)   # tergite overlap: each somite slightly fuller mid-length
            secs.append(section(0.0010-u*(Ls+0.0010),sw+bulge,st-0.004+bulge,sb-0.004,20,car,0.0010))
        bm=loft(secs)
        if i<5:
            for s in (-1,1):
                pb=Vector((-Ls*0.40,0.0024*s,SB[i]-0.0040+0.0008)); pm=pb+Vector((0.0010,0.0004*s,-0.0028))
                tube([pb,pm],0.00070,0.00060,6,bm)
                for ry,lr,wd in ((0.0007,0.0058,0.0024),(-0.0007,0.0050,0.0020)):
                    blade([pm+Vector((0.0004,ry*s,0)),pm+Vector((0.0018+wd*0.3,ry*s,-lr*0.45)),pm+Vector((0.0014,ry*s,-lr)),pm+Vector((-0.0006,ry*s,-lr*0.9)),pm+Vector((-wd*0.5,ry*s,-lr*0.4)),pm+Vector((-0.0004,ry*s,0))],0.00030,bm)
        o=obj('Abd%d'%(i+1),bm,M_body,parent,(0.0 if i==0 else -SOM[i-1],0,0.004 if i==0 else 0.0))
        o.rotation_euler=(0,rest_flex,0)   # natural resting arch (ventral flexion)
        abd.append(o); parent=o
    # tail fan: pointed telson with dorsal groove + paired uropods (endopod, exopod)
    bm=blade([Vector((0,0.0020,0)),Vector((-0.010,0.0015,-0.0004)),Vector((-0.0185,0.0003,-0.0009)),Vector((-0.0198,0,-0.0010)),Vector((-0.0185,-0.0003,-0.0009)),Vector((-0.010,-0.0015,-0.0004)),Vector((0,-0.0020,0))],0.0012,None,axis='z')
    for s in (-1,1):
        for ang,L,w in ((math.radians(16),0.0168,0.0048),(math.radians(27),0.0192,0.0056)):
            d=Vector((-math.cos(ang),math.sin(ang)*s,0)); n=Vector((d.y,-d.x,0))*(-s)
            o0=Vector((0,0.0020*s,-0.0003))
            blade([o0,o0+d*L*0.35+n*w*0.55,o0+d*L*0.85+n*w*0.45,o0+d*L,o0+d*L*0.8-n*w*0.35,o0+d*L*0.3-n*w*0.3],0.0005,bm,axis='z')
    tail=obj('TailFan',bm,M_fan,abd[-1],(-SOM[-1],0,-0.0030))
    tail.rotation_euler=(0,rest_flex*0.5,0)
    return root
