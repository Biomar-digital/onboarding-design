# Higgsfield 3D Jutsu edit (rev 26 -> 27): the farmer throws once (release ~f160, throw T1) and the camera follows that throw.
import bpy
D=bpy.data
def allfc(o):
    ad=o.animation_data; r=[]
    if not ad or not ad.action: return r
    for L in ad.action.layers:
        for s in L.strips:
            for cb in s.channelbags: r+=list(cb.fcurves)
    return r
def rekey(fc,keys,interp='BEZIER'):
    fc.keyframe_points.clear(); fc.keyframe_points.add(len(keys))
    for kp,(f,v) in zip(fc.keyframe_points,keys):
        kp.co=(f,v); kp.interpolation=interp; kp.handle_left_type=kp.handle_right_type='AUTO_CLAMPED'
    fc.update()
sh=D.objects['FARMER_ArmR_Shoulder']
for fc in allfc(sh):
    if fc.data_path!='rotation_quaternion': continue
    pts=[(k.co[0],k.co[1]) for k in fc.keyframe_points]; rest=pts[0][1]
    rekey(fc,[(97,rest),(140,rest)]+[(f,v) for f,v in pts if 148<=f<=170]+[(180,rest)])
tp=D.objects['FARMER_Torso_Pivot']
for fc in allfc(tp):
    if fc.data_path=='rotation_euler' and fc.array_index==2:
        pts=[(k.co[0],k.co[1]) for k in fc.keyframe_points]
        rekey(fc,[(97,0.0),(140,0.0)]+[(f,v) for f,v in pts if 148<=f<=166]+[(176,0.0)])
for fc in allfc(D.objects['FARMER_Scoop_Load']):
    if fc.data_path=='scale': rekey(fc,[(1,1.0),(160,1.0),(162,0.0)],'CONSTANT')
for o in D.objects:
    n=o.name
    if (n.startswith('FEED_Air_') or n.startswith('FEED_Splash_')) and n.split('_')[2] in ('T0','T2','T3'):
        for fc in allfc(o):
            if fc.data_path=='scale': rekey(fc,[(1,0.0),(360,0.0)],'CONSTANT')
            if fc.data_path=='hide_render': rekey(fc,[(1,1.0),(360,1.0)],'CONSTANT')
        o.scale=(0,0,0); o.hide_render=True
