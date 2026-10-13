import bpy, sys, math
sys.path.insert(0,'/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/film')
import drive
from mathutils import Vector, Matrix
S=drive.S
bpy.ops.wm.open_mainfile(filepath=S+'film/film.blend')
st=drive.states([100]); drive.apply(st[100],drive.Shrimp()); bpy.context.view_layer.update()
before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=S+'hf/hand.glb'); new=[o for o in bpy.data.objects if o not in before]
h=[o for o in new if o.type=='MESH'][0]; h.name='HAND_NEW'
for o in new:
    if o is not h: bpy.data.objects.remove(o)
h.parent=None; h.matrix_world=Matrix.Identity(4)
tip_l=min((v.co for v in h.data.vertices),key=lambda c:c.x).copy()
btn=bpy.data.objects['PHONE_Stop_Button'].matrix_world.translation
tipW=btn+Vector((0,0,0.004))
sl=bpy.data.objects['HAND_Forearm_Sleeve']; slc=sum((sl.matrix_world@v.co for v in sl.data.vertices),Vector())/len(sl.data.vertices)
u=(slc-tipW); u.z=0; u.normalize(); u=(u+Vector((0,0,float(sys.argv[-2])))).normalized()
p=Vector((0,0,-1)); p=(p-u*p.dot(u)).normalized()
Xw=u; Zw=-p; Yw=Zw.cross(Xw)
R=Matrix((Xw,Yw,Zw)).transposed().to_4x4()
s=float(sys.argv[-1])/(max(v.co.x for v in h.data.vertices)-tip_l.x)
h.matrix_world=Matrix.Translation(tipW)@R@Matrix.Scale(s,4)@Matrix.Translation(-tip_l)
root=bpy.data.objects['HAND_Root']; mw=h.matrix_world.copy(); h.parent=root; h.matrix_world=mw
bpy.data.objects['HAND_Skin'].hide_render=True; bpy.data.objects['HAND_Forearm_Sleeve'].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=S+'film/film.blend'); print('HAND_OK',s,tip_l)
