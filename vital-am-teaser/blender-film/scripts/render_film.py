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
for F in todo:
    t=time.time(); drive.apply(st[F],sh); sc.render.filepath=OUT+'/f%04d.jpg'%F
    bpy.ops.render.render(write_still=True); print('FRAME',F,st[F]['shot'],round(time.time()-t,1),flush=True)
