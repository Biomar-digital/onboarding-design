# Hero SmartCare VITAL AM, enfoque v3: base en una FOTO REAL mitad dentro / mitad fuera del agua (Adobe Stock 380471108,
# amanecer con ola y menisco reales), recortada a vertical. Debajo de la linea el agua sigue limpia y profunda (se quita
# el fondo de arena con la raya), y se montan los camarones reales de las fotos del cliente (recortes/), graduados a la
# luz y el color del agua, mas alimento cayendo en diagonal desde la superficie bajo el sol hacia el camaron principal.
# Exporta PSD con capas + JPG.   python armar_hero_v3.py FOTO_STOCK CARPETA_RECORTES SALIDA_SIN_EXTENSION [--psd]
import sys, numpy as np
from PIL import Image, ImageFilter, ImageDraw
STOCK, CUT, OUT = sys.argv[1:4]
W, H = 2000, 3000
rng = np.random.default_rng(5)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def rgba(c, a): return np.concatenate([np.clip(c, 0, 1), np.clip(a, 0, 1)[..., None]], -1).astype(np.float32)
def blur(a, r):
    a = np.clip(a, 0, 1); ch = a.shape[2] if a.ndim == 3 else 1; a3 = a if a.ndim == 3 else a[..., None]
    o = np.stack([np.asarray(Image.fromarray((a3[..., i] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(float(r))), np.float32) / 255 for i in range(ch)], -1)
    return o if a.ndim == 3 else o[..., 0]
def noise(scale, seed):                                                         # ruido suave de baja frecuencia
    r = np.random.default_rng(seed); s = max(2, int(scale))
    n = r.random((int(s * H / W) + 2, s + 2)).astype(np.float32)
    return np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
# ---- foto base, recorte vertical centrado en el sol
st = np.asarray(Image.open(STOCK).convert('RGB'), np.float32) / 255           # 3872x2592
X0, Y0 = 613, 350; ph = min(H, st.shape[0] - Y0)
photo = np.zeros((H, W, 3), np.float32); photo[:ph] = st[Y0:Y0 + ph, X0:X0 + W]
SUN = (1000, 344)
# linea del agua por columna: ultima fila clara (menisco) antes del agua turquesa, entre y=950 y y=1800
lum = blur(photo, 3).mean(-1)[950:1800]                                        # menisco claro (>0.5) / agua (~0.3)
line = 950 + (lum.shape[0] - 1 - np.argmax((lum > 0.45)[::-1], 0)).astype(np.float32)
xs_ = np.arange(W); ok = np.ones(W, bool)                                         # curva suave (domo): ajuste robusto de grado 2
for _ in range(5): cf = np.polyfit(xs_[ok], line[ok], 2); ok = np.abs(line - np.polyval(cf, xs_)) < 25
line = np.polyval(cf, xs_).astype(np.float32)
k = 61; line = np.convolve(np.pad(line, k // 2, mode='edge'), np.ones(k) / k, 'valid')
LW = line[None, :]
dy = yy - LW                                                                    # >0 bajo la linea
# ---- 1) agua profunda (bajo la foto): color tomado justo bajo la linea y llevado a azul profundo
top_c = np.stack([np.median(photo[(line + 60 + i).astype(int).clip(0, H - 1), np.arange(W)], 0) for i in range(0, 60, 6)]).mean(0)
d = np.clip(dy / (H - 1100), 0, 1)[..., None]
deep = np.array([0.02, 0.16, 0.30])
water = top_c * (1 - d) ** 1.3 + deep * (1 - (1 - d) ** 1.3)
water *= (0.9 + 0.2 * (noise(6, 1) - 0.5) + 0.12 * (noise(18, 2) - 0.5))[..., None]   # variacion suave del agua
glow = np.exp(-(((xx - SUN[0]) / 650) ** 2 + ((yy - 1150) / 900) ** 2))[..., None] # luz que entra bajo el sol
water = np.clip(water + glow * np.array([0.30, 0.26, 0.16]) * 0.45, 0, 1)
layers = [('01 Agua profunda', rgba(water, np.ones((H, W))), 'normal')]
# ---- 2) foto real (cielo, ola, menisco y primera franja de agua) que se funde con el agua profunda
fade = 1 - np.clip((dy - 45) / 110, 0, 1)
ph_soft = photo.copy(); bl = blur(photo, 18); w2 = np.clip((dy - 15) / 50, 0, 1)[..., None]
ph_soft = ph_soft * (1 - w2) + bl * w2                                          # desenfoca la arena antes de desaparecer
layers.append(('02 Foto real: amanecer y linea del agua (Adobe Stock)', rgba(ph_soft, fade * (yy < ph)), 'normal'))
# ---- 3) rayos de sol que siguen bajo el agua
ang = np.arctan2(xx - SUN[0], yy - SUN[1]); s = np.zeros_like(ang)
for i in range(14): s += np.maximum(np.sin(ang * rng.uniform(16, 60) + rng.uniform(0, 6.28)), 0) ** rng.uniform(2, 5) * rng.uniform(0.3, 1)
s /= s.max(); fall = np.clip(1 - dy / 1700, 0, 1) ** 1.5 * np.clip(dy / 60, 0, 1) * np.exp(-(ang / 0.75) ** 2)
layers.append(('03 Rayos de sol bajo el agua', rgba(np.ones((H, W, 3)) * np.array([1.0, 0.92, 0.72]), blur(s * fall * 0.26, 14)), 'screen'))
# ---- camarones reales del cliente, graduados al agua
def shrimp(name, width, angle, flip=False):
    im = Image.open(f'{CUT}/{name}'); im = im.crop(im.getchannel('A').getbbox())
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS).rotate(angle, resample=Image.BICUBIC, expand=True)
    return np.asarray(im, np.float32) / 255
def place(canvas, sp, cx, cy):
    h, w = sp.shape[:2]; x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    src = sp[ya - y0:yb - y0, xa - x0:xb - x0]; dst = canvas[ya:yb, xa:xb]
    a = src[..., 3:4]; dst[..., :3] = dst[..., :3] * (1 - a) + src[..., :3] * a; dst[..., 3:4] = dst[..., 3:4] * (1 - a) + a
def grade(sp, cx, cy, haze, warm):
    c = sp[..., :3]; L = c.mean(-1, keepdims=True)
    wc = water[int(np.clip(cy, 0, H - 1)), int(np.clip(cx, 0, W - 1))]
    c = np.clip((c - 0.5) * 1.25 + 0.56, 0, 1) * np.array([0.95, 1.0, 1.0]) * 0.95 + wc * 0.12   # algo de contraste y el tono del agua
    hh = np.linspace(1, 0, c.shape[0])[:, None, None]                              # luz desde arriba (calida, del amanecer)
    c = c * (0.85 + 0.25 * hh) + warm * hh * np.array([0.10, 0.07, 0.02])
    c = c * (1 - haze) + np.clip(wc * 1.35 + 0.05, 0, 1) * haze                   # distancia: se pierde en el agua
    a = sp[..., 3:4] * (0.78 + 0.22 * np.clip(L * 1.6, 0, 1))                     # cuerpo translucido: deja ver algo de agua
    al = a[..., 0]; rim = np.clip(al - np.roll(al, 6, 0), 0, 1)[..., None]          # borde de arriba iluminado (luz del sol)
    c = np.clip(c + rim * np.array([0.35, 0.30, 0.20]) * (1 - haze), 0, 1)
    return np.concatenate([np.clip(c, 0, 1), a * (1 - 0.55 * haze)], -1)
bgL = np.zeros((H, W, 4), np.float32)
for name, wd, an, fl, cx, cy, hz, b in (('bg1.png', 560, 22, False, 300, 1500, 0.45, 6), ('bg1.png', 440, 15, False, 1760, 2250, 0.5, 8),
                                         ('hero.png', 380, 32, False, 1380, 2620, 0.6, 11), ('hero.png', 460, -12, True, 1800, 1750, 0.45, 6),
                                         ('bg1.png', 320, 28, False, 700, 2080, 0.62, 12)):
    sp = grade(shrimp(name, wd, an, fl), cx, cy, hz, 0.4); sp = np.concatenate([blur(sp[..., :3], b), blur(sp[..., 3], b)[..., None]], -1)
    place(bgL, sp, cx, cy)
layers.append(('04 Camarones de fondo (fotos reales)', bgL, 'normal'))
heroL = np.zeros((H, W, 4), np.float32)
HX, HY = 1080, 1720
sp = grade(shrimp('hero.png', 1500, 30), HX, HY, 0.12, 1.0); sp[..., :3] = blur(sp[..., :3], 0.6)
place(heroL, sp, HX, HY)
layers.append(('05 Camaron principal (foto real)', heroL, 'normal'))
# ---- 6) alimento cayendo desde la superficie bajo el sol hacia la cabeza del camaron
pel = Image.new('RGBA', (W, H), (0, 0, 0, 0))
A = np.array([900.0, line[900] + 70]); B = np.array([1430.0, 1250.0])
for i in range(34):
    t = rng.uniform(0, 1) ** 0.9; p = A + (B - A) * t + rng.normal(0, 25 + 35 * t, 2) * np.array([1.0, 0.8])
    Lp = float(rng.uniform(16, 28) * (1.1 - 0.2 * t)); Dp = Lp * 0.6; sz = int(Lp * 2 + 10)
    yv, xv = np.mgrid[0:sz, 0:sz].astype(np.float32) - sz / 2
    ins = ((np.abs(xv) < Lp / 2) & (np.abs(yv) < Dp / 2)) | ((((np.abs(xv) - Lp / 2) ** 2 + yv ** 2) < (Dp / 2) ** 2) & (np.abs(xv) >= Lp / 2))
    sh = 0.55 + 0.6 * np.clip(1 - (yv + Dp / 2) / Dp, 0, 1)
    c = np.array([0.36, 0.24, 0.13])[None, None] * (sh[..., None] + rng.normal(0, 0.05, (sz, sz, 1)))
    a = np.concatenate([np.clip(c, 0, 1), ins[..., None] * 1.0], -1)
    im = Image.fromarray((a * 255).astype(np.uint8), 'RGBA').rotate(float(rng.uniform(0, 180)), resample=Image.BICUBIC)
    b = float(rng.choice([0, 0, 0.7, 1.5, 3])); im = im.filter(ImageFilter.GaussianBlur(b)) if b else im
    pel.alpha_composite(im, (int(p[0] - sz / 2), int(p[1] - sz / 2)))
pel = np.asarray(pel, np.float32) / 255; pel[..., 3] *= np.clip((dy - 25) / 25, 0, 1)        # solo bajo la superficie
layers.append(('06 Alimento cayendo', pel, 'normal'))
# ---- 7) particulas en suspension (fuera de foco) + 8) vineta y profundidad para el titular
pa = np.zeros((H, W), np.float32)
for i in range(260):
    x, y = rng.uniform(0, W), rng.uniform(1150, H); r = rng.uniform(1.2, 4.5); pa[int(y) % H, int(x) % W] = rng.uniform(0.4, 1)
pa = blur(np.clip(blur(pa, 1.5) * 9, 0, 1), 1.2) * (dy > 40)
layers.append(('07 Particulas en el agua', rgba(np.ones((H, W, 3)) * np.array([0.85, 0.95, 0.95]), pa * 0.3), 'screen'))
r2 = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.42) / (H * 0.75)) ** 2
va = np.clip((r2 - 0.3) * 0.7, 0, 0.45) + np.clip((yy - 0.70 * H) / (0.30 * H), 0, 1) * 0.30
layers.append(('08 Vineta y profundidad', rgba(np.zeros((H, W, 3)) + np.array([0.0, 0.04, 0.09]), va), 'normal'))
# ---- vista previa y PSD
comp = np.zeros((H, W, 3), np.float32)
for _, Ly, mode in layers:
    a = Ly[..., 3:4]; c = Ly[..., :3]
    comp = comp * (1 - a) + ((1 - (1 - comp) * (1 - c)) if mode == 'screen' else c) * a
Image.fromarray((np.clip(comp, 0, 1) * 255).astype(np.uint8)).save(OUT + '.jpg', quality=92)
if '--psd' in sys.argv:
    import packbits, pytoshop.codecs as _pc; _pc.packbits = packbits
    from pytoshop import enums
    from pytoshop.user import nested_layers as nl
    from pytoshop.image_data import ImageData
    BM = {'normal': enums.BlendMode.normal, 'screen': enums.BlendMode.screen}
    pl = []
    for name, Ly, mode in reversed(layers):
        u8 = (np.clip(Ly, 0, 1) * 255).astype(np.uint8)
        pl.append(nl.Image(name=name, visible=True, opacity=255, blend_mode=BM[mode], top=0, left=0, bottom=H, right=W,
                           channels={0: u8[..., 0], 1: u8[..., 1], 2: u8[..., 2], -1: u8[..., 3]}))
    psd = nl.nested_layers_to_psd(pl, enums.ColorMode.rgb, size=(W, H), compression=enums.Compression.rle)
    cu8 = (np.clip(comp, 0, 1) * 255).astype(np.uint8)
    psd.image_data = ImageData(channels=np.stack([cu8[..., 0], cu8[..., 1], cu8[..., 2]]), compression=enums.Compression.rle)
    with open(OUT + '.psd', 'wb') as fd: psd.write(fd)
print('OK', line[[0, 1000, 1999]])
