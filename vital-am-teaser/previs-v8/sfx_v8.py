# Reference sound bed for previs v8 (15 s): muffled alarm underwater -> clear phone alarm, cut on the tap (f85),
# dawn pond ambience + paddlewheels, shovel whooshes and splashes, underwater rumble, swell on the reveal.
import numpy as np, wave
SR=48000; D=15.0; t=np.arange(int(SR*D))/SR; rng=np.random.default_rng(3); noise=rng.standard_normal(len(t))
def lp(x,a):
    y=np.empty_like(x); acc=0.0
    for i,v in enumerate(x): acc+=a*(v-acc); y[i]=acc
    return y
def env(t0,t1,fi=0.02,fo=0.05): return np.clip((t-t0)/fi,0,1)*np.clip((t1-t)/fo,0,1)
F=lambda f:(f-1)/24
beep=np.sin(2*np.pi*1760*t)*((t*4%1)<0.5)
out=lp(beep*env(F(18),F(48)),0.04)*0.5 + beep*env(F(49),F(85),0.005,0.01)*0.26
under=lp(noise,0.004)*2.0; out+=under*(env(0,F(48),0.3,0.05)+env(F(196),F(316),0.05,0.2))
air=lp(noise,0.05)*0.06; out+=air*(env(F(97),F(196),0.2,0.05)+env(F(316),D,0.2,0.5))
# one scoop sweep (release ~f160), pellet rain hitting the surface while the camera chases it, the plunge, muffled plops below
out+=lp(noise,0.25)*np.sin(np.clip((t-F(156))/0.3,0,1)*np.pi)*0.24*env(F(156),F(164))
for st in range(183,195,1): out+=lp(noise,0.6)*np.exp(-np.clip(t-F(st),0,None)*22)*(t>F(st))*0.10
out+=lp(noise,0.15)*np.exp(-np.clip(t-F(195),0,None)*6)*(t>F(195))*0.5
for st in list(range(199,214,3)): out+=lp(noise,0.08)*np.exp(-np.clip(t-F(st),0,None)*14)*(t>F(st))*0.30
out+=(np.sin(2*np.pi*110*t)*0.06+np.sin(2*np.pi*165*t)*0.04)*np.clip((t-F(301))/3,0,1)
out=out/np.max(np.abs(out))*0.8
w=wave.open('sfx_v8.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
