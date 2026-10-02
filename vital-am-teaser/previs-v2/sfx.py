# Reference sound bed for the v2 previs (not final audio): muffled alarm underwater -> clear alarm on the phone,
# cut on the tap, pond morning ambience, shovel whoosh, splashes, underwater rumble, swell on the reveal.
import numpy as np, wave
SR=48000; D=10.0; t=np.arange(int(SR*D))/SR; out=np.zeros_like(t)
rng=np.random.default_rng(3)
def lp(x,a):            # one-pole low-pass
    y=np.empty_like(x); acc=0.0
    for i,v in enumerate(x): acc+=a*(v-acc); y[i]=acc
    return y
def env(t0,t1,fi=0.02,fo=0.05):
    e=np.clip((t-t0)/fi,0,1)*np.clip((t1-t)/fo,0,1); return e
beep=np.sin(2*np.pi*1760*t)*((t*4%1)<0.5)            # 2 beeps per second pattern
alarm_u=lp(beep*env(0.8,1.5),0.04)*0.5                  # S1: muffled through the water
alarm_c=beep*env(1.5,2.54,0.005,0.01)*0.28              # S2: clear, cut on the tap (f61)
noise=rng.standard_normal(len(t))
under=lp(noise,0.004)*2.2*(env(0,1.5,0.3,0.05)+env(5.5,8.0,0.05,0.2))
air=lp(noise,0.05)*0.05*env(3.0,5.5,0.2,0.05)+lp(noise,0.05)*0.05*env(8.0,10,0.2,0.5)
whoosh=lp(noise,0.2)*np.sin(np.clip((t-4.75)/0.35,0,1)*np.pi)*0.25*env(4.75,5.1)
splash=sum(lp(noise,0.5)*np.exp(-np.clip(t-st,0,None)*18)*(t>st)*0.25 for st in (5.3,5.38,5.47,5.55))
swell=np.sin(2*np.pi*110*t)*0.06*np.clip((t-8)/2,0,1)+np.sin(2*np.pi*165*t)*0.04*np.clip((t-8.5)/1.5,0,1)
out=alarm_u+alarm_c+under+air+whoosh+splash+swell
out=out/np.max(np.abs(out))*0.8
w=wave.open('sfx_v2.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
