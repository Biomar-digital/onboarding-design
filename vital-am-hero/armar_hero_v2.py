# Hero SmartCare VITAL AM, enfoque v2: una sola foto real bajo el agua como base (la foto de los camarones: misma agua,
# misma luz, camarones reales con su desenfoque natural), unida en la linea del agua con la foto real del amanecer
# sobre los estanques. Retoque: agua clara azul, luz de amanecer entrando desde la superficie (rayos y brillo calido),
# alimento cayendo en diagonal desde la superficie hacia el camaron principal y mas profundidad abajo para el titular.
# Exporta PSD con capas + JPG de vista previa.   python armar_hero_v2.py CARPETA_FOTOS SALIDA_SIN_EXTENSION
import sys, numpy as np
from PIL import Image, ImageFilter
FOT, OUT = sys.argv[1:3]
W, H = 2000, 3000; WL = 1000; SUN = (1030, 690)
rng = np.random.default_rng(7)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def rgba(c, a): return np.concatenate([np.clip(c, 0, 1), np.clip(a, 0, 1)[..., None]], -1).astype(np.float32)
def blur(a, r): return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), np.float32) / 255
layers = []
# ---- 1) amanecer real sobre los estanques (arriba del agua)
s = 1.25; sky = np.asarray(Image.open(f'{FOT}/49.jpg').convert('RGB').resize((int(2000 * s), int(1333 * s)), Image.LANCZOS), np.float32) / 255
oy = SUN[1] - int(560 * s); ox = (sky.shape[1] - W) // 2                     # sol de la foto (y~560) en SUN
top = np.zeros((H, W, 3), np.float32); y0 = max(0, oy); y1 = min(H, oy + sky.shape[0])
top[y0:y1] = sky[y0 - oy:y1 - oy, ox:ox + W]
layers.append(('01 Amanecer y estanques (foto)', rgba(top, (yy < WL + 3).astype(np.float32)), 'normal'))
# ---- 2) foto real bajo el agua, regradeada a agua clara azul, con mas profundidad abajo
Z = 1.35                                                                     # acercamiento: el camaron principal gana protagonismo
im47 = Image.open(f'{FOT}/47.jpg').convert('RGB'); im47 = im47.resize((int(2000 * Z), int(1500 * Z)), Image.LANCZOS)
cx = int(1180 * Z) - 1000                                                     # centra al camaron principal (x~1180 en la foto)
uw = np.asarray(im47.crop((cx, 0, cx + 2000, 1500)), np.float32) / 255        # 2000x1500, superficie arriba
base = np.zeros((H, W, 3), np.float32); base[WL:WL + 1500] = uw
rest = H - WL - 1500; base[WL + 1500:] = blur(uw[::-1][:rest], 30)              # continua hacia abajo, fuera de foco
L = base.mean(-1, keepdims=True); d = np.clip((yy - WL) / (H - WL), 0, 1)[..., None]
tint = np.array([0.18, 0.54, 0.70]) * (1 - d) + np.array([0.02, 0.15, 0.29]) * d
bg = blur(base, 45) + 1e-3                                                     # luz de fondo de la foto
rel = np.clip(base / bg, 0, 2.5)                                               # el camaron relativo al agua que lo rodea
water = tint * (0.55 + 0.6 * bg.mean(-1, keepdims=True))
graded = np.clip(water * rel ** 1.6, 0, 1)
own = np.clip(base * (water.mean(-1, keepdims=True) / np.maximum(L, 1e-3)), 0, 1)        # color propio del camaron (rojos, amarillos)
mask = np.clip((np.abs(rel - 1).max(-1, keepdims=True) - 0.06) * 4, 0, 1)
graded = graded * (1 - 0.45 * mask) + own * 0.45 * mask
glow = np.exp(-(((xx - SUN[0]) / 720) ** 2 + ((yy - WL) / 640) ** 2))[..., None]
graded = np.clip(graded + glow * np.array([0.52, 0.36, 0.13]) * 0.6, 0, 1)
graded *= (1 - 0.38 * np.clip((yy - 2250) / 750, 0, 1))[..., None]
layers.append(('02 Bajo el agua (foto real retocada)', rgba(graded, (yy >= WL).astype(np.float32)), 'normal'))
# ---- 3) rayos de sol que siguen bajo el agua
ang = np.arctan2(xx - SUN[0], yy - (WL - 420)); st = np.zeros_like(ang)
for k in range(9): st += np.maximum(np.sin(ang * rng.uniform(18, 70) + rng.uniform(0, 6.28)), 0) ** rng.uniform(3, 8) * rng.uniform(0.3, 1)
st /= st.max(); fall = np.clip(1 - (yy - WL) / 1700, 0, 1) ** 1.6 * (yy > WL) * np.exp(-(ang / 0.8) ** 2)
layers.append(('03 Rayos de sol', rgba(np.ones((H, W, 3)) * np.array([1.0, 0.93, 0.75]), blur(st * fall * 0.45, 7)), 'screen'))
# ---- 4) alimento cayendo desde la superficie (bajo el sol) hacia la cabeza del camaron principal
from PIL import ImageDraw
pel = Image.new('RGBA', (W, H), (0, 0, 0, 0))
A = np.array([1120.0, WL + 30]); B = np.array([1720.0, WL + 380])                 # cabeza del camaron principal ~ (1700, WL+320)
for i in range(38):
    t = rng.uniform(0, 1) ** 0.85; p = A + (B - A) * t + rng.normal(0, 25 + 70 * t, 2) * np.array([1.0, 0.5])
    Lp = float(rng.uniform(11, 20) * (1.1 - 0.25 * t)); Dp = Lp * 0.55; sz = int(Lp * 2 + 8)
    yv, xv = np.mgrid[0:sz, 0:sz].astype(np.float32) - sz / 2
    inside = ((np.abs(xv) < Lp / 2) & (np.abs(yv) < Dp / 2)) | ((((np.abs(xv) - Lp / 2) ** 2 + yv ** 2) < (Dp / 2) ** 2) & (np.abs(xv) >= Lp / 2))
    sh = 0.6 + 0.5 * np.clip(1 - (yv + Dp / 2) / Dp, 0, 1)
    c = np.array([0.55, 0.38, 0.20])[None, None] * (sh[..., None] + rng.normal(0, 0.05, (sz, sz, 1)))
    a = np.concatenate([np.clip(c, 0, 1), inside[..., None] * 1.0], -1)
    im = Image.fromarray((a * 255).astype(np.uint8), 'RGBA').rotate(float(rng.uniform(0, 180)), resample=Image.BICUBIC)
    b = float(rng.choice([0, 0, 0.6, 1.5, 3]));  im = im.filter(ImageFilter.GaussianBlur(b)) if b else im
    pel.alpha_composite(im, (int(p[0] - sz / 2), int(p[1] - sz / 2)))
layers.append(('04 Alimento cayendo', np.asarray(pel, np.float32) / 255, 'normal'))
# ---- 5) superficie del agua (linea con brillo y reflejo del sol por debajo)
wave = WL + 4 * np.sin(xx / 85) + 2 * np.sin(xx / 21 + 1.3)
band = np.exp(-((yy - wave) / 4) ** 2); under = np.exp(-((yy - wave - 18) / 14) ** 2) * (yy > wave) * (0.4 + 0.6 * np.exp(-((xx - SUN[0]) / 480) ** 2))
layers.append(('05 Superficie del agua', rgba(np.ones((H, W, 3)) * np.array([1.0, 0.95, 0.86]), band * 0.75 + under * 0.35), 'screen'))
# ---- 6) vineta suave
r2 = ((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H * 0.42) / (H * 0.72)) ** 2
layers.append(('06 Vineta', rgba(np.zeros((H, W, 3)) + np.array([0.0, 0.03, 0.07]), np.clip((r2 - 0.3) * 0.8, 0, 0.5)), 'normal'))
# ---- vista previa y PSD
comp = np.zeros((H, W, 3), np.float32)
for name, Ly, mode in layers:
    a = Ly[..., 3:4]; c = Ly[..., :3]
    comp = comp * (1 - a) + ((1 - (1 - comp) * (1 - c)) if mode == 'screen' else c) * a
Image.fromarray((np.clip(comp, 0, 1) * 255).astype(np.uint8)).save(OUT + '_preview.jpg', quality=92)
if '--psd' in sys.argv:
    import packbits, pytoshop.codecs as _pc; _pc.packbits = packbits      # pytoshop usa packbits para comprimir (RLE)
    from pytoshop import enums
    from pytoshop.user import nested_layers as nl
    BM = {'normal': enums.BlendMode.normal, 'screen': enums.BlendMode.screen}
    pl = []
    for name, Ly, mode in reversed(layers):
        u8 = (np.clip(Ly, 0, 1) * 255).astype(np.uint8)
        pl.append(nl.Image(name=name.strip(), visible=True, opacity=255, blend_mode=BM[mode], top=0, left=0, bottom=H, right=W,
                           channels={0: u8[..., 0], 1: u8[..., 1], 2: u8[..., 2], -1: u8[..., 3]}))
    psd = nl.nested_layers_to_psd(pl, enums.ColorMode.rgb, size=(W, H), compression=enums.Compression.rle)
    from pytoshop.image_data import ImageData                                 # imagen combinada (vista previa del PSD en Finder/Bridge)
    cu8 = (np.clip(comp, 0, 1) * 255).astype(np.uint8)
    psd.image_data = ImageData(channels=np.stack([cu8[..., 0], cu8[..., 1], cu8[..., 2]]), compression=enums.Compression.rle)
    with open(OUT + '.psd', 'wb') as fd: psd.write(fd)
print('OK')
