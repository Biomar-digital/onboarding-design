import bpy, sys, os, time
sys.path.insert(0,'/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/film')
import drive
S=drive.S
a=sys.argv[sys.argv.index('--')+1:]; A,Bf=int(a[0]),int(a[1]); W=int(a[2]); SAMP=int(a[3]); OUT=a[4]
bpy.ops.wm.open_mainfile(filepath=S+'film/film.blend')
sc=bpy.context.scene; sc.render.resolution_x=W; sc.render.resolution_y=W*9//16; sc.cycles.samples=SAMP
os.makedirs(OUT,exist_ok=True)
todo=[F for F in range(A,Bf+1) if not os.path.exists(OUT+'/f%04d.jpg'%F)]
if not todo: print('NOTHING'); sys.exit()
st=drive.states(todo); sh=drive.Shrimp()
import json, copy
for F in todo:
    t=time.time()
    if F in drive.SPLIT:
        meta={}
        for fo in ('air','under'):
            d=copy.deepcopy(st[F]); d['force']=fo; drive.apply(d,sh)
            sc.render.filepath=OUT+'/f%04d_%s.jpg'%(F,fo[0]); bpy.ops.render.render(write_still=True)
        cm=bpy.context.scene.camera.matrix_world
        cz=drive.CAM_SMOOTH.get(str(F),(st[F]['cam'],0))[0][13]
        if drive.CAM_FIX and 262<=F<=332:   # pellet ride: waterline from the new camera height
            import camfix; cz=camfix.cam_A(F)[0].translation.z
        if drive.CAM_FIX and 448<=F<=484 and __import__('camfix').RISE_ON:   # hand-built rise: waterline from the new camera height
            import camfix; cz=camfix.cam_B(F).translation.z
        right=cm.to_3x3()@drive.Vector((1,0,0))
        json.dump({'z':cz,'roll':__import__('math').atan2(right.z,(right.x**2+right.y**2)**0.5)},open(OUT+'/f%04d.json'%F,'w'))
        import shutil; shutil.copy(OUT+'/f%04d_u.jpg'%F,OUT+'/f%04d.jpg'%F)
    else:
        drive.apply(st[F],sh); sc.render.filepath=OUT+'/f%04d.jpg'%F; bpy.ops.render.render(write_still=True)
    print('FRAME',F,st[F]['shot'],round(time.time()-t,1),flush=True)
