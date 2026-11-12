# Banda de sonido sintetizada para el video del fry (11 s, 25 fps). Todo generado con numpy/scipy: no usa grabaciones.
#   python3 sonido_fry.py salida.wav
# Los tiempos salen de los mismos numeros que fry_escena.py (frames de diseno -> frames reales con FT).
import sys, numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000; FPS = 25; NF = 275; TS = 1.2; E0, E1 = 178, 236
def FT(x): return 1 + (x - 1) * TS                                   # frame de diseno -> frame real
def T(frame): return (frame - 1) / FPS                               # frame real -> segundos
N = int(NF / FPS * SR); t = np.arange(N) / SR
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def place(sig, t0, gain=1.0, pan=0.0):
    """suma una senal mono en t0 (s) con paneo -1..1"""
    i0 = int(t0 * SR)
    if i0 >= N: return
    if i0 < 0: sig = sig[-i0:]; i0 = 0
    sig = sig[:N - i0]; gl = gain * np.cos((pan + 1) * np.pi / 4); gr = gain * np.sin((pan + 1) * np.pi / 4)
    L[i0:i0 + len(sig)] += sig * gl; R[i0:i0 + len(sig)] += sig * gr

def smooth(x, a, b): return np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))
def lp(x, fc, order=2): return signal.sosfilt(signal.butter(order, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, order=2): return signal.sosfilt(signal.butter(order, fc, 'high', fs=SR, output='sos'), x)
def bp(x, f1, f2, order=2): return signal.sosfilt(signal.butter(order, [f1, f2], 'band', fs=SR, output='sos'), x)
def noise(n): return rng.standard_normal(n)
def brown(n):
    b = np.cumsum(noise(n)); b = hp(b, 20); return b / (np.abs(b).max() + 1e-9)

def bubble(r, dur=None):
    """burbuja de aire (resonancia de Minnaert): tono que sube de afinacion y se apaga rapido. r en unidades de escena"""
    f0 = np.clip(11.0 / r, 380, 2600)                                # mas grande = mas grave
    dur = dur or np.clip(0.05 + r * 4.5, 0.05, 0.2); n = int(dur * SR); tt = np.arange(n) / SR
    f = f0 * (1 + 0.55 * (tt / dur) ** 1.6); ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-tt / (dur * 0.33)) * smooth(tt, 0, 0.004)
    return np.sin(ph) * env + 0.25 * np.sin(2 * ph) * env ** 2

def sweep_noise(dur, f_a, f_b, q=2.0):
    """ruido con un filtro pasa-banda que se desliza (soplido / whoosh)"""
    n = int(dur * SR); x = noise(n); out = np.zeros(n); blk = 256
    zi = None
    for i in range(0, n, blk):
        u = i / n; fc = f_a * (f_b / f_a) ** u
        sos = signal.butter(2, [fc / q ** 0.5, min(fc * q ** 0.5, SR * 0.45)], 'band', fs=SR, output='sos')
        if zi is None: zi = signal.sosfilt_zi(sos) * 0
        out[i:i + blk], zi = signal.sosfilt(sos, x[i:i + blk], zi=zi)
    return out

# ---------------------------------------------------------------- 1) ambiente bajo el agua: rumor grave + textura suave
amb = lp(brown(N), 180) * 0.9 + lp(bp(noise(N), 300, 1200), 900) * 0.06
amb *= 0.5 + 0.2 * np.sin(2 * np.pi * 0.11 * t) + 0.15 * np.sin(2 * np.pi * 0.07 * t + 1)
amb2 = lp(brown(N), 160) * 0.9
amb_env = smooth(t, 0, 0.8) * (1 - smooth(t, T(E1 - 20), T(E1 - 6)))
L += amb * amb_env * 0.22; R += (0.6 * amb + 0.4 * amb2) * amb_env * 0.22

# ---------------------------------------------------------------- 2) entrada: el coleteo mueve agua (swish por cada batido) + estela de burbujitas
ph = 0.0
for F in range(1, int(FT(60))):
    f = 1 + (F - 1) / TS; sp = (1 - min(1.0, max(0.0, (f - 1) / 58))) ** 1.2
    freq = 0.7 + 2.1 * sp ** 0.6; ph_new = ph + 2 * np.pi * freq / FPS
    for k in (0, 1):                                                 # dos impulsos de agua por ciclo de cola
        if int((ph + k * np.pi) / (2 * np.pi)) != int((ph_new + k * np.pi) / (2 * np.pi)) and F > 8:
            sw = sweep_noise(0.16, 260, 620, 2.5) * np.hanning(int(0.16 * SR))
            place(sw, T(F), 0.10 * sp ** 0.6, pan=-0.75 + 1.0 * (1 - sp))
    ph = ph_new
r2 = np.random.default_rng(21)
for i in range(18):                                                  # burbujitas de la estela
    f0 = FT(8 + i * 2.3 + r2.uniform(-0.8, 0.8)); r = r2.uniform(0.004, 0.009)
    place(bubble(r), T(f0) + r2.uniform(0, 0.08), 0.035, pan=-0.7 + 0.9 * i / 18)

# ---------------------------------------------------------------- 3) burbujas que suelta por la boca
for f0d, r, pan in ((60, 0.020, 0.15), (65, 0.011, 0.2), (70, 0.027, 0.25), (76, 0.014, 0.2), (81, 0.009, 0.3)):
    place(bubble(r), T(FT(f0d)), 0.30, pan)
    place(bubble(r * 1.25), T(FT(f0d)) + 0.045, 0.10, pan + 0.1)     # eco chiquito: se despega

# ---------------------------------------------------------------- 4) infla el globo: toma aire + tres soplidos con goma que se estira
for k, (b0, b1) in enumerate(((89.5, 98.5), (100, 108.5), (110, 119))):
    ti = T(FT(b0 - 5)); di = T(FT(b0)) - ti                          # toma de aire: ruido suave que sube
    inh = sweep_noise(di, 500, 1500, 3.0) * np.hanning(int(di * SR)) ** 0.8
    place(inh, ti, 0.05, 0.15)
    tb = T(FT(b0)); db = T(FT(b1)) - tb; n = int(db * SR); tt = np.arange(n) / SR; u = tt / db
    air = sweep_noise(db, 700 + 120 * k, 1500 + 250 * k, 2.2)        # aire entrando
    env = smooth(u, 0, 0.12) * (1 - smooth(u, 0.7, 1.0))
    fr = (150 + 45 * k) * (1 + 0.5 * u ** 1.3) * (1 + 0.012 * np.sin(2 * np.pi * 23 * tt))   # goma: tono que sube con vibrato
    php = 2 * np.pi * np.cumsum(fr) / SR
    rub = (np.sin(php) + 0.5 * np.sin(2 * php + 0.4) + 0.25 * np.sin(3 * php)) * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * tt) ** 2)
    place(air * env, tb, 0.085, 0.3); place(lp(rub, 900) * env, tb, 0.07, 0.35)
ts = T(FT(90) + 34); n = int(0.35 * SR); tt = np.arange(n) / SR      # asentado: "boing" de goma chiquito
boing = np.sin(2 * np.pi * np.cumsum(240 * (1 + 0.18 * np.exp(-tt / 0.06) * np.cos(2 * np.pi * 9 * tt))) / SR) * np.exp(-tt / 0.09)
place(boing, ts, 0.09, 0.4)

# ---------------------------------------------------------------- 5) final: el globo crece (lento -> acelera) hasta tapar todo, y "pop" suave al blanco
t0 = T(E0); d = T(E1 - 8) - t0; n = int(d * SR); tt = np.arange(n) / SR; u = tt / d; k = u ** 2.6
air = sweep_noise(d, 350, 2400, 2.5); rumble = lp(brown(n), 140)
fr = 95 * (1 + 2.6 * k) * (1 + 0.01 * np.sin(2 * np.pi * 19 * tt)); php = 2 * np.pi * np.cumsum(fr) / SR
rub = lp(np.sin(php) + 0.5 * np.sin(2 * php + 0.3) + 0.3 * np.sin(3 * php + 1), 1200)
env = (0.06 + 0.94 * u ** 2.2) * smooth(u, 0, 0.06)
place(air * env, t0, 0.20, 0.2); place(rumble * env, t0, 0.55, 0.0); place(rub * env * (0.7 + 0.3 * np.sin(2 * np.pi * 27 * tt) ** 2), t0, 0.10, 0.25)
for j, uu in enumerate((0.18, 0.36, 0.5, 0.62, 0.72, 0.80)):         # crujidos de goma estirandose, cada vez mas seguidos
    c = bp(noise(int(0.05 * SR)), 900, 2600) * np.exp(-np.arange(int(0.05 * SR)) / SR / 0.012)
    place(c, t0 + uu * d, 0.05 + 0.03 * j / 5, 0.3 - 0.1 * j)
tp = t0 + d                                                          # llega al blanco: golpe grave blando + aire que se abre + cola
n = int(1.2 * SR); tt = np.arange(n) / SR
thump = np.sin(2 * np.pi * np.cumsum(70 * (1 + 1.2 * np.exp(-tt / 0.03))) / SR) * np.exp(-tt / 0.16)
burst = lp(noise(n), 3500) * np.exp(-tt / 0.10) * smooth(tt, 0, 0.004)
shim = lp(hp(noise(n), 1500), 6000) * np.exp(-tt / 0.45) * smooth(tt, 0, 0.05)
place(thump, tp, 0.50, 0.0); place(burst, tp, 0.16, 0.0); place(shim, tp, 0.035, -0.3); place(shim[::-1].copy()[::-1] * 0.9, tp + 0.01, 0.035, 0.3)

# ---------------------------------------------------------------- mezcla: reverb corta "bajo el agua", filtro general, limitador suave
def reverb(x, wet=0.22, dur=0.9, seed=3):
    r = np.random.default_rng(seed); n = int(dur * SR); ir = r.standard_normal(n) * np.exp(-np.arange(n) / SR / 0.22); ir = lp(ir, 2600)
    ir /= np.sqrt((ir ** 2).sum()); y = signal.fftconvolve(x, ir)[:len(x)]; return x + wet * y
L = reverb(L, seed=3); R = reverb(R, seed=4)
L = lp(L, 7000); R = lp(R, 7000)                                     # el agua se come los agudos
L = hp(L, 28); R = hp(R, 28)
peak = max(np.abs(L).max(), np.abs(R).max()); g = 0.82 / peak
L = np.tanh(L * g * 1.15) / np.tanh(1.15) * 0.82; R = np.tanh(R * g * 1.15) / np.tanh(1.15) * 0.82
fade = smooth(t, 0, 0.05) * (1 - smooth(t, NF / FPS - 0.35, NF / FPS - 0.02))
out = np.stack([L * fade, R * fade], axis=1)
wavfile.write(sys.argv[1] if len(sys.argv) > 1 else 'fry_sonido.wav', SR, (out * 32767).astype(np.int16))
print('ok', out.shape, 'pico', float(np.abs(out).max()))
