# Reference sound bed for previs v3 (15 s): muffled alarm underwater -> clear phone alarm, cut on the tap (f85),
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
under=lp(noise,0.004)*2.0; out+=under*(env(0,F(48),0.3,0.05)+env(F(181),F(316),0.05,0.2))
air=lp(noise,0.05)*0.06; out+=air*(env(F(97),F(180),0.2,0.05)+env(F(316),D,0.2,0.5))
for T in (150,166): out+=lp(noise,0.2)*np.sin(np.clip((t-F(T-6))/0.35,0,1)*np.pi)*0.22*env(F(T-6),F(T+3))
for st in (169,172,176,185,188,192): out+=lp(noise,0.5)*np.exp(-np.clip(t-F(st),0,None)*16)*(t>F(st))*0.2
out+=(np.sin(2*np.pi*110*t)*0.06+np.sin(2*np.pi*165*t)*0.04)*np.clip((t-F(301))/3,0,1)
out=out/np.max(np.abs(out))*0.8
w=wave.open('sfx_v3.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
