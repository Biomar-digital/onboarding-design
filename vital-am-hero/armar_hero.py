# Hero image SmartCare VITAL AM (sin textos ni logos): fotos reales compuestas por capas.
# Arriba del agua: amanecer real sobre estanques; abajo: agua clara azul con rayos de sol que siguen bajo la superficie,
# alimento cayendo en diagonal hacia el camaron protagonista (foto real recortada), camarones de fondo mas suaves.
# Exporta el PSD con capas editables + un JPG de vista previa.
# python armar_hero.py CARPETA_FOTOS CARPETA_RECORTES SALIDA_SIN_EXTENSION
import sys, math, numpy as np
from PIL import Image, ImageFilter, ImageDraw
FOT, CUT, OUT = sys.argv[1:4]
W, H = 2000, 3000
WL = 1060                                          # linea del agua
SUN = (1040, 760)                                  # sol en el horizonte
rng = np.random.default_rng(4)
def blank(): return np.zeros((H, W, 4), np.float32)
def from_pil(im, x, y, canvas=None):
    c = blank() if canvas is None else canvas
    a = np.asarray(im.convert('RGBA'), np.float32) / 255
    h, w = a.shape[:2]; x0, y0 = int(x), int(y)
    xs, ys = max(0, -x0), max(0, -y0); xe, ye = min(w, W - x0), min(h, H - y0)
    if xe <= xs or ye <= ys: return c
    src = a[ys:ye, xs:xe]; dst = c[y0 + ys:y0 + ye, x0 + xs:x0 + xe]
    al = src[..., 3:4]; out_a = al + dst[..., 3:4] * (1 - al)
    dst[..., :3] = np.where(out_a > 0, (src[..., :3] * al + dst[..., :3] * dst[..., 3:4] * (1 - al)) / np.maximum(out_a, 1e-6), 0)
    dst[..., 3:4] = out_a; return c
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
layers = []                                        # (nombre, rgba float 0..1, modo)
# ---- 1) cielo y estanques (foto real), solo arriba de la linea del agua
sky = Image.open(f'{FOT}/49.jpg').convert('RGB')
s = 1.12; sky = sky.resize((int(2000 * s), int(1333 * s)), Image.LANCZOS)
skyl = from_pil(sky, -(sky.width - W) / 2, 15)
skyl[WL:, :, 3] = 0
# calidez de amanecer un poco mas marcada
skyl[..., 0] = np.clip(skyl[..., 0] * 1.04, 0, 1); skyl[..., 2] *= 0.95
layers.append(('01 Amanecer y estanques (foto)', skyl, 'normal'))
# ---- 2) agua: gradiente de turquesa iluminado (arriba) a azul profundo (abajo), brillo del sol bajo la superficie
d = np.clip((yy - WL) / (H - WL), 0, 1)
top = np.array([0.20, 0.55, 0.62]); mid = np.array([0.04, 0.30, 0.45]); bot = np.array([0.01, 0.10, 0.20])
col = np.where(d[..., None] < 0.4, top + (mid - top) * (d[..., None] / 0.4), mid + (bot - mid) * ((d[..., None] - 0.4) / 0.6))
glow = np.exp(-(((xx - SUN[0]) / 650) ** 2 + ((yy - WL) / 520) ** 2))[..., None]
col = col + glow * np.array([0.55, 0.45, 0.22]) * 0.55
water = np.concatenate([np.clip(col, 0, 1), (yy >= WL).astype(np.float32)[..., None]], -1)
layers.append(('02 Agua (degradado)', water, 'normal'))
# ---- 3) rayos de sol bajo el agua: abanico desde el sol, con variacion angular, se apagan con la profundidad
ang = np.arctan2(xx - SUN[0], yy - (WL - 380)); r = np.hypot(xx - SUN[0], yy - (WL - 380))
streak = np.zeros_like(ang)
for k in range(9):
    f = rng.uniform(18, 70); ph = rng.uniform(0, 6.28); streak += np.maximum(np.sin(ang * f + ph), 0) ** rng.uniform(3, 8) * rng.uniform(0.3, 1)
streak /= streak.max()
fall = np.clip(1 - (yy - WL) / 1700, 0, 1) ** 1.6 * (yy > WL) * np.exp(-((ang) / 0.75) ** 2)
rays = np.zeros((H, W, 4), np.float32); rays[..., :3] = np.array([1.0, 0.92, 0.72]); rays[..., 3] = np.clip(streak * fall * 0.55, 0, 1)
rays_im = Image.fromarray((rays * 255).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(6))
layers.append(('03 Rayos de sol (pantalla)', np.asarray(rays_im, np.float32) / 255, 'screen'))
# ---- 4) camarones de fondo: recortes reales, chicos, desenfocados y teñidos de azul (profundidad)
def shrimp_layer(name, specs):
    c = blank()
    for f, scale, rot, flip, cx, cy, blur, fade in specs:
        im = Image.open(f'{CUT}/{f}.png').convert('RGBA')
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)
        a = np.asarray(im, np.float32) / 255
        depth_col = np.array([0.08, 0.32, 0.45]); a[..., :3] = a[..., :3] * (1 - fade) + depth_col * fade   # se pierde en el azul
        a[..., 3] *= 0.92
        im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGBA')
        if blur: im = im.filter(ImageFilter.GaussianBlur(float(blur)))
        c = from_pil(im, cx - im.width / 2, cy - im.height / 2, c)
    return c
far = shrimp_layer('lejos', [('bg1', 0.32, 18, False, 360, 1500, 5, 0.72), ('bg3', 0.30, 30, True, 1650, 1980, 6, 0.75), ('bg2', 0.26, 5, False, 1500, 2600, 6, 0.78),
                             ('bg1', 0.28, -12, True, 260, 2150, 6, 0.78), ('bg3', 0.26, 22, False, 820, 1290, 5, 0.70), ('bg2', 0.24, -8, True, 1820, 1460, 5, 0.70)])
layers.append(('04 Camarones fondo lejos', far, 'normal'))
mid_ = shrimp_layer('medio', [('bg2', 0.46, 12, False, 380, 1820, 3, 0.45), ('bg1', 0.50, 25, True, 1640, 2330, 3, 0.48), ('bg3', 0.44, 35, False, 980, 2780, 4, 0.55)])
layers.append(('05 Camarones fondo medio', mid_, 'normal'))
# ---- 5) particulas en suspension
pc = blank(); im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
for _ in range(900):
    x, y = rng.uniform(0, W), rng.uniform(WL + 10, H); r_ = rng.choice([1, 1, 1.5, 2, 3]); a_ = int(rng.uniform(40, 150) * (1 - (y - WL) / (H - WL) * 0.6))
    dr.ellipse([x - r_, y - r_, x + r_, y + r_], fill=(220, 235, 230, a_))
im = im.filter(ImageFilter.GaussianBlur(1.2))
layers.append(('06 Particulas', np.asarray(im, np.float32) / 255, 'normal'))
# ---- 6) alimento cayendo: pellets cilindricos marron, trayectoria diagonal desde la superficie hacia el camaron
pel = Image.new('RGBA', (W, H), (0, 0, 0, 0))
def pellet(cx, cy, L, Dm, rot, blur, light):
    sz = int(L * 2 + 8); p = Image.new('RGBA', (sz, sz), (0, 0, 0, 0)); a = np.zeros((sz, sz, 4), np.float32)
    y_, x_ = np.mgrid[0:sz, 0:sz].astype(np.float32) - sz / 2
    inside = (np.abs(x_) < L / 2) & (np.abs(y_) < Dm / 2) | (((np.abs(x_) - L / 2) ** 2 + y_ ** 2) < (Dm / 2) ** 2) & (np.abs(x_) >= L / 2)
    sh = 0.55 + 0.45 * np.clip(1 - (y_ + Dm / 2) / Dm, 0, 1)               # luz desde arriba
    grain = rng.normal(0, 0.06, (sz, sz))
    base = np.array([0.42, 0.26, 0.13])
    a[..., :3] = np.clip(base[None, None] * (sh[..., None] + grain[..., None]) * light + np.array([0.1, 0.08, 0.03]) * (light - 0.8), 0, 1); a[..., 3] = inside
    p = Image.fromarray((a * 255).astype(np.uint8), 'RGBA').rotate(rot, resample=Image.BICUBIC)
    if blur: p = p.filter(ImageFilter.GaussianBlur(float(blur)))
    pel.alpha_composite(p, (int(cx - sz / 2), int(cy - sz / 2)))
A = np.array([1240, WL + 40]); B = np.array([1700, 1330])
for i in range(46):
    t = rng.uniform(0, 1) ** 0.8; p = A + (B - A) * t + rng.normal(0, 30 + 90 * t, 2) * np.array([1.0, 0.6])
    L = rng.uniform(14, 26) * (1.15 - 0.3 * t); depthblur = rng.choice([0, 0, 0, 1, 2, 4])
    pellet(p[0], p[1], L, L * 0.55, rng.uniform(0, 180), depthblur, 1.05 - 0.25 * t)
layers.append(('07 Alimento cayendo', np.asarray(pel, np.float32) / 255, 'normal'))
# ---- 7) camaron protagonista: recorte real, girado subiendo hacia el alimento, con luz de amanecer desde arriba
hero = Image.open(f'{CUT}/hero.png').convert('RGBA')
hs = 1.08; hero = hero.resize((int(hero.width * hs), int(hero.height * hs)), Image.LANCZOS)
ha = np.asarray(hero, np.float32) / 255
hh, hw = ha.shape[:2]; vy = np.linspace(0, 1, hh)[:, None, None]
warm = np.array([1.08, 0.98, 0.86]); cool = np.array([0.80, 0.93, 1.02])
ha[..., :3] = np.clip(ha[..., :3] * (warm * (1 - vy) + cool * vy), 0, 1)          # calido arriba, frio abajo
ha[..., :3] = np.clip((ha[..., :3] - 0.5) * 1.12 + 0.5 + 0.02, 0, 1)                # mas contraste
al = Image.fromarray((ha[..., 3] * 255).astype(np.uint8)); er = al.filter(ImageFilter.MinFilter(7))
rim = np.clip((np.asarray(al, np.float32) - np.asarray(er, np.float32)) / 255, 0, 1) * (1 - vy[..., 0]) ** 1.5   # borde iluminado arriba
ha[..., :3] = np.clip(ha[..., :3] + rim[..., None] * np.array([0.45, 0.38, 0.22]), 0, 1)
hero = Image.fromarray((ha * 255).astype(np.uint8), 'RGBA').rotate(30, expand=True, resample=Image.BICUBIC)
hx, hy = 1080 - hero.width / 2, 1690 - hero.height / 2
shadow = hero.split()[3].filter(ImageFilter.GaussianBlur(40)); sh = Image.new('RGBA', hero.size, (0, 20, 35, 0)); sh.putalpha(shadow.point(lambda v: int(v * 0.35)))
layers.append(('08 Sombra suave protagonista', from_pil(sh, hx + 30, hy + 60), 'multiply'))
layers.append(('09 Camaron protagonista', from_pil(hero, hx, hy), 'normal'))
# ---- 8) superficie: linea del agua con brillo, reflejo del sol en la cara inferior (ventana de Snell)
surf = blank()
wave = WL + 6 * np.sin(xx / 90) + 3 * np.sin(xx / 23 + 1.3)
band = np.exp(-((yy - wave) / 5) ** 2); under = np.exp(-((yy - wave - 22) / 18) ** 2) * (yy > wave)
surf[..., :3] = np.array([1.0, 0.95, 0.85]); surf[..., 3] = np.clip(band * 0.8 + under * 0.35 * (0.5 + 0.5 * np.exp(-((xx - SUN[0]) / 500) ** 2)), 0, 1)
layers.append(('10 Superficie del agua', surf, 'screen'))
# ---- 9) burbujas junto a la superficie
bub = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(bub)
for _ in range(70):
    x, y = rng.uniform(0, W), WL + rng.exponential(110) + 10; r_ = rng.uniform(2, 9)
    dr.ellipse([x - r_, y - r_, x + r_, y + r_], outline=(235, 250, 255, int(rng.uniform(90, 200))), width=1)
    dr.ellipse([x - r_ * 0.5, y - r_ * 0.6, x - r_ * 0.1, y - r_ * 0.2], fill=(255, 255, 255, 160))
layers.append(('11 Burbujas', np.asarray(bub.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255, 'normal'))
# ---- 10) vineta y profundidad (abajo mas oscuro: lugar para el titular)
vig = blank(); r2 = ((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2
vig[..., :3] = np.array([0.0, 0.04, 0.08]); vig[..., 3] = np.clip((r2 - 0.25) * 0.9, 0, 0.6) + np.clip((yy - 2300) / 700, 0, 1) * 0.25 * (yy > WL)
layers.append(('12 Vineta', vig, 'normal'))
# ---------------------------------------------------------------- composicion de vista previa
comp = np.zeros((H, W, 3), np.float32)
for name, L_, mode in layers:
    a = L_[..., 3:4]; c = L_[..., :3]
    if mode == 'screen': res = 1 - (1 - comp) * (1 - c)
    elif mode == 'multiply': res = comp * c
    else: res = c
    comp = comp * (1 - a) + res * a
Image.fromarray((np.clip(comp, 0, 1) * 255).astype(np.uint8)).save(OUT + '_preview.jpg', quality=92)
# ---------------------------------------------------------------- PSD con capas
from pytoshop import enums
from pytoshop.user import nested_layers as nl
BM = {'normal': enums.BlendMode.normal, 'screen': enums.BlendMode.screen, 'multiply': enums.BlendMode.multiply}
psd_layers = []
for name, L_, mode in reversed(layers):                       # arriba primero
    u8 = (np.clip(L_, 0, 1) * 255).astype(np.uint8)
    ch = {0: u8[..., 0], 1: u8[..., 1], 2: u8[..., 2], -1: u8[..., 3]}
    psd_layers.append(nl.Image(name=name, visible=True, opacity=255, blend_mode=BM[mode], top=0, left=0, bottom=H, right=W, channels=ch))
psd = nl.nested_layers_to_psd(psd_layers, enums.ColorMode.rgb, size=(H, W), compression=enums.Compression.rle)
with open(OUT + '.psd', 'wb') as fd: psd.write(fd)
print('OK', OUT)
