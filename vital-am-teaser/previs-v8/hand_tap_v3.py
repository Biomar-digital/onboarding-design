# Higgsfield 3D Jutsu edit (rev 24 -> 25): pointing hand for shot 2; index pad lands on PHONE_Stop_Button at f84. Rev 26 then removed HAND_Nails and trimmed the wrist stub inside the sleeve.
import bpy, bmesh, math
from mathutils import Vector, Matrix, Quaternion
D=bpy.data; sc=bpy.context.scene
root=D.objects['HAND_Root']; col=root.users_collection[0]
for n in ('HAND_Skin','HAND_Nails'):
    o=D.objects.get(n)
    if o: me=o.data; D.objects.remove(o,do_unlink=True); D.meshes.remove(me)
btn=D.objects['PHONE_Stop_Button']; sc.frame_set(84)
tgt=root.matrix_world.inverted()@btn.matrix_world.translation
# hand frame (HAND_Root local): fingers -Y, palm -Z, thumb side -X; whole hand pitched fingers-down about the wrist
PITCH=math.radians(26); WR=Vector((0,0.045,0.0))
Rp=Matrix.Rotation(PITCH,4,'X')
def H(v): return WR+(Rp@(v-WR).to_4d()).to_3d()
MCP={'index':Vector((-0.026,-0.050,-0.002)),'middle':Vector((-0.008,-0.055,-0.001)),'ring':Vector((0.010,-0.052,-0.002)),'little':Vector((0.026,-0.045,-0.004))}
LEN={'index':(0.040,0.025,0.019),'middle':(0.045,0.028,0.020),'ring':(0.042,0.026,0.019),'little':(0.033,0.020,0.017)}
RAD={'index':(0.0100,0.0090,0.0080),'middle':(0.0103,0.0093,0.0082),'ring':(0.0098,0.0088,0.0078),'little':(0.0088,0.0079,0.0071)}
FLEX={'index':(12,16,10),'middle':(88,108,60),'ring':(92,108,60),'little':(95,104,60)}
SPL={'index':-0.06,'middle':0.0,'ring':0.06,'little':0.14}
def chain(k):
    base=MCP[k]; s=SPL[k]; d0=Vector((math.sin(s),-math.cos(s),0)); pts=[base.copy()]; a=0.0
    for L,th in zip(LEN[k],FLEX[k]):
        a+=math.radians(th); d=Vector((d0.x*math.cos(a),d0.y*math.cos(a),-math.sin(a))); pts.append(pts[-1]+d*L)
    return [H(p) for p in pts]
ch={k:chain(k) for k in MCP}
# fingertip pad of the index (slightly palmar of the distal end)
pi=ch['index']; dd=(pi[3]-pi[2]).normalized()
pad=pi[3]-dd*0.004+(Rp@Vector((0,0,-1,0))).to_3d()*RAD['index'][2]*0.9
OFF=tgt-pad
mb=D.metaballs.new('HAND_MB3'); mb.resolution=0.0022; mb.render_resolution=0.0022; mb.threshold=0.6
mo=D.objects.new('HAND_MB3_tmp',mb); col.objects.link(mo); mo.parent=root; mo.matrix_parent_inverse=Matrix.Identity(4)
def cap(p0,p1,r,st=2.0):
    p0=p0+OFF; p1=p1+OFF
    e=mb.elements.new(); e.type='CAPSULE'; e.co=(p0+p1)/2; d=p1-p0; L=d.length
    e.size_x=max(L/2,1e-4); e.radius=r; e.stiffness=st
    e.rotation=Vector((1,0,0)).rotation_difference(d.normalized()) if L>1e-6 else Quaternion()
def ell(c,r,sx,sy,sz,st=2.0):
    e=mb.elements.new(); e.type='ELLIPSOID'; e.co=H(c)+OFF; e.radius=r; e.size_x=sx; e.size_y=sy; e.size_z=sz; e.stiffness=st
    e.rotation=Rp.to_quaternion()
# palm: dorsum flatter, padded palmar side, thenar/hypothenar pads
ell(Vector((0.0,-0.008,0.0)),0.038,0.88,1.15,0.34,2.4)
ell(Vector((-0.001,-0.020,-0.007)),0.029,0.95,0.85,0.30,1.8)
ell(Vector((-0.028,-0.002,-0.010)),0.019,0.9,1.3,0.7,1.8)
ell(Vector((0.028,0.002,-0.009)),0.016,0.8,1.5,0.6,1.6)
for k,c in MCP.items(): cap(H(c+Vector((0,0.034,0.001))),H(c),RAD[k][0]*1.30,2.0)
ell(Vector((0.0,-0.040,0.002)),0.036,1.0,0.55,0.34,2.2)   # knuckle row, smooth dorsum
ell(Vector((0.0,-0.018,0.003)),0.036,0.95,0.75,0.30,2.0)
cap(H(Vector((0,0.040,0.0))),Vector((0,0.115,0.004)),0.027,2.0)   # wrist into the sleeve (unpitched end)
for k,p in ch.items():
    for i in range(3): cap(p[i],p[i+1],RAD[k][i]*1.30,2.2)
# thumb resting along the curled middle finger
t0=Vector((-0.024,0.016,-0.010)); t1=t0+Vector((-0.010,-0.024,-0.017)); t2=t1+Vector((0.007,-0.024,-0.011)); t3=t2+Vector((0.010,-0.017,-0.004))
T=[H(t) for t in (t0,t1,t2,t3)]
cap(T[0],T[1],0.0140,2.0); cap(T[1],T[2],0.0122,2.2); cap(T[2],T[3],0.0108,2.2)
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get(); me=D.meshes.new_from_object(mo.evaluated_get(dg)); me.name='HAND_Skin_Mesh'
D.objects.remove(mo,do_unlink=True); D.metaballs.remove(mb)
bm=bmesh.new(); bm.from_mesh(me)
for _ in range(3): bmesh.ops.smooth_vert(bm,verts=bm.verts,factor=0.5,use_axis_x=True,use_axis_y=True,use_axis_z=True)
bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
me.materials.clear(); me.materials.append(D.materials['MAT_Farmer_Skin'])
ho=D.objects.new('HAND_Skin',me); col.objects.link(ho); ho.parent=root; ho.matrix_parent_inverse=Matrix.Identity(4)
# nails
nail=D.materials.get('MAT_Hand_Nail')
bm=bmesh.new()
tips={k:(p[2],p[3],RAD[k][2]*1.30) for k,p in ch.items()}; tips['thumb']=(T[2],T[3],0.0108)
for k,(p0,p1,r) in tips.items():
    d=(p1-p0).normalized(); side=d.cross(Vector((0,0,1))).normalized(); nrm=side.cross(d).normalized()
    if nrm.z<0: nrm=-nrm
    if k=='thumb': nrm=(nrm+Vector((-0.6,0,0))).normalized(); side=d.cross(nrm).normalized()
    L=(p1-p0).length; c=p0+d*L*0.60+nrm*r*0.93+OFF; w=r*0.62
    vs=[]
    for i in range(5):
        for j in range(5):
            u=(i/4-0.5)*2; v=j/4
            vs.append(bm.verts.new(c+side*u*w+d*(v-0.45)*L*0.62-nrm*(u*u)*r*0.30))
    for i in range(4):
        for j in range(4): bm.faces.new((vs[i*5+j],vs[(i+1)*5+j],vs[(i+1)*5+j+1],vs[i*5+j+1]))
nm=D.meshes.new('HAND_Nails_Mesh'); bm.to_mesh(nm); bm.free(); nm.materials.append(nail)
for p in nm.polygons: p.use_smooth=True
no=D.objects.new('HAND_Nails',nm); col.objects.link(no); no.parent=root; no.matrix_parent_inverse=Matrix.Identity(4)
# sleeve follows the wrist offset
sl=D.objects['HAND_Forearm_Sleeve']; sl.location=sl.location+Vector((OFF.x,OFF.y,OFF.z*0.5))
hres=dict(off=[round(v,4) for v in OFF],verts=len(me.vertices),sleeve=[round(v,3) for v in sl.location])

