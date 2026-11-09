# Une las dos pasadas del hero 3D (arriba / abajo del agua) en la linea del agua y exporta JPG + PSD con capas:
# arriba del agua, bajo el agua, linea de superficie, rayos de sol en el agua y vineta (lugar para el titular).
# python unir_hero.py CARPETA_RENDER SALIDA_SIN_EXTENSION
import sys, json, numpy as np
from PIL import Image, ImageFilter
D, OUT = sys.argv[1:3]
air = np.asarray(Image.open(f'{D}/hero_air.png').convert('RGB'), np.float32) / 255
und = np.asarray(Image.open(f'{D}/hero_under.png').convert('RGB'), np.float32) / 255
H, W = air.shape[:2]; wl = json.load(open(f'{D}/waterline.json'))['wl'] * H
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
k = W / 2000.0
# ---- linea del agua realista (como en fotos mitad dentro / mitad fuera del agua):
# borde ondulado e irregular de la superficie + leve curva (domo de la carcasa), una franja de menisco donde la imagen
# se estira y desenfoca, borde oscuro con brillo fino arriba, y gotas en el vidrio sobre la linea.
rngw = np.random.default_rng(11); xs = np.arange(W, dtype=np.float32)
# 1) superficie vista desde arriba (franja entre la orilla y la linea): espejo calmo del cielo y los arboles, con ondas
#    suaves que lo rompen al acercarse (antes salia un azul oscuro plano, poco creible)
yh = int(wl) - 1
while yh > wl - 0.25 * H and np.median(air[yh, :, 2] - air[yh, :, 0]) > 0.0: yh -= 1
yh += 1                                                                              # primera fila de agua bajo la orilla
if wl - yh > 4:
    ry = np.arange(yh, int(wl) + int(40 * k) + 1); t = (ry - yh) / max(wl - yh, 1)       # 0 en la orilla, 1 en la linea
    rip = np.zeros((len(ry), W), np.float32)
    for f_, a_ in ((1 / (70 * k), 1.0), (1 / (23 * k), 0.6), (1 / (9 * k), 0.35)):
        rip += a_ * np.sin(2 * np.pi * f_ * xs[None] + rngw.uniform(0, 6.28) + (ry[:, None] - yh) * rngw.uniform(0.6, 1.4) / k)
    srcx = np.clip(xs[None] + rip * (1 + 5 * t[:, None]) * k, 0, W - 1).astype(int)
    srcy = np.clip(2 * yh - ry[:, None] - (rip * 0.6 * t[:, None] * k), 0, H - 1).astype(int)
    refl = air[srcy, srcx]
    refl = np.asarray(Image.fromarray((refl * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2 * k)), np.float32) / 255
    fres = (0.78 - 0.18 * t)[:, None, None]                                           # mas espejo lejos, algo menos cerca
    refl = refl * fres + air[ry] * (1 - fres) * 0.6 + np.array([0.0, 0.01, 0.02]) * 0.5
    fade = np.clip((ry - yh) / (2.5 * k), 0, 1)[:, None, None]                          # transicion suave con la orilla
    air = air.copy(); air[ry] = air[ry] * (1 - fade) + refl * fade
# 2) linea del agua: curva amplia y suave (domo de la carcasa) con ondulacion lenta, sin dientes
wv = np.zeros(W, np.float32)
for f_, a_ in ((1 / (560 * k), 6 * k), (1 / (210 * k), 2.6 * k), (1 / (95 * k), 0.9 * k)):
    wv += a_ * np.sin(2 * np.pi * f_ * xs + rngw.uniform(0, 6.28))
wv += 10 * k * ((xs - W / 2) / (W / 2)) ** 2 - 4 * k + 3 * k * (xs / W - 0.5)         # curva del domo + leve inclinacion
wave = wl + wv[None, :] + 0 * yy
BW = 26 * k                                                                          # ancho del menisco
def resample(img, ymap):
    y0 = np.clip(np.floor(ymap).astype(int), 0, H - 2); fy = np.clip(ymap - y0, 0, 1)[..., None]
    xi = np.broadcast_to(np.arange(W), ymap.shape)
    return img[y0, xi] * (1 - fy) + img[y0 + 1, xi] * fy
dy = yy - wave; ady = np.abs(dy)
st_u = np.where((dy > 0) & (dy < BW), wave + BW * (ady / BW) ** 0.6, yy)               # abajo: la franja junto a la linea se estira (lente de agua)
st_a = np.where((dy < 0) & (dy > -BW * 0.5), wave - BW * 0.5 * (ady / (BW * 0.5)) ** 0.7, yy)
und2 = resample(und, st_u); air2 = resample(air, st_a)
bl_u = np.asarray(Image.fromarray((und2 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4 * k)), np.float32) / 255
bl_a = np.asarray(Image.fromarray((air2 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3 * k)), np.float32) / 255
wb_u = np.clip(1 - dy / BW, 0, 1)[..., None] * (dy > 0)[..., None]; und2 = und2 * (1 - wb_u) + bl_u * wb_u
wb_a = np.clip(1 + dy / (BW * 0.5), 0, 1)[..., None] * (dy < 0)[..., None]; air2 = air2 * (1 - wb_a) + bl_a * wb_a
# 3) cara inferior de la superficie: espejo (reflexion total) del fondo, claro y calido, que se apaga hacia abajo
TB = 30 * k
mir = resample(bl_u, np.where((dy > 0) & (dy < TB), wave + TB + (TB - dy) * 1.4, yy))
wm = (np.clip(1 - dy / TB, 0, 1) ** 1.5 * (dy > 0) * 0.5)[..., None]
und2 = und2 * (1 - wm) + np.clip(mir * 1.25 + np.array([0.06, 0.05, 0.03]), 0, 1) * wm
m = np.clip(dy / (1.5 * k) + 0.5, 0, 1)
# gotas en el vidrio, justo arriba de la linea: refractan (imagen invertida y desenfocada) con borde oscuro y brillo
drop = np.zeros((H, W), np.float32); drop_img = air2.copy()
for _ in range(16):
    cx = rngw.uniform(0, W); r = rngw.uniform(4, 12) * k; cy = wl + wv[int(min(cx, W - 1))] - rngw.uniform(2, 70) * k * (1 if rngw.random() < 0.8 else 2.5)
    x0, x1, y0_, y1_ = int(max(0, cx - r - 2)), int(min(W, cx + r + 3)), int(max(0, cy - r - 2)), int(min(H, cy + r + 3))
    if x1 <= x0 or y1_ <= y0_: continue
    sy_, sx_ = np.mgrid[y0_:y1_, x0:x1].astype(np.float32); dd = np.hypot(sx_ - cx, (sy_ - cy) * 1.15) / r
    inside = dd < 1
    srcy = np.clip(cy - (sy_ - cy) * 3.0, 0, H - 1).astype(int); srcx = np.clip(cx - (sx_ - cx) * 3.0, 0, W - 1).astype(int)
    lens = bl_a[srcy, srcx] * 0.85 + 0.08
    edge = np.clip((dd - 0.7) / 0.3, 0, 1)[..., None]
    hl = np.exp(-(((sx_ - cx + 0.35 * r) / (0.18 * r)) ** 2 + ((sy_ - cy + 0.35 * r) / (0.18 * r)) ** 2))[..., None]
    val = lens * (1 - 0.55 * edge) + hl * 0.8
    region = drop_img[y0_:y1_, x0:x1]; region[inside] = val[inside]; drop[y0_:y1_, x0:x1][inside] = 1
air2 = drop_img
L_air = np.concatenate([air2, (1 - m)[..., None]], -1)
L_und = np.concatenate([und2, np.ones((H, W, 1), np.float32)], -1)
# brillo de la superficie: linea fina + reflejo suave por debajo
band = np.exp(-((dy + 2.5 * k) / (1.3 * k)) ** 2) * 0.6 + np.exp(-((dy - 12 * k) / (9 * k)) ** 2) * (dy > 0) * 0.12   # brillo fino arriba del borde + reflejo suave abajo
L_surf = np.concatenate([np.ones((H, W, 3)) * np.array([1.0, 0.96, 0.88]), band[..., None]], -1).astype(np.float32)
dark = np.exp(-((dy - 0.8 * k) / (1.8 * k)) ** 2) * 0.45                             # borde del menisco: linea oscura y algo verdosa
L_edge = np.concatenate([np.zeros((H, W, 3)) + np.array([0.05, 0.10, 0.09]), dark[..., None]], -1).astype(np.float32)
# rayos de sol que siguen bajo el agua desde el sol (busca el punto mas brillante del cielo)
sky = air[: int(wl) - 2].mean(-1); skyb = np.asarray(Image.fromarray((sky * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(20 * k)))
sy, sx = np.unravel_index(np.argmax(skyb), sky.shape)
ang = np.arctan2(xx - sx, yy - sy); rng = np.random.default_rng(3); st = np.zeros_like(ang)
for _ in range(10): st += np.maximum(np.sin(ang * rng.uniform(25, 80) + rng.uniform(0, 6.28)), 0) ** rng.uniform(3, 8) * rng.uniform(0.3, 1)
st /= st.max(); fall = np.clip(1 - (yy - wl) / (0.55 * H), 0, 1) ** 1.5 * (dy > 4 * k) * np.exp(-(ang / 0.6) ** 2)
ray_a = np.asarray(Image.fromarray((np.clip(st * fall * 0.35, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5 * k)), np.float32) / 255
L_rays = np.concatenate([np.ones((H, W, 3)) * np.array([1.0, 0.93, 0.76]), ray_a[..., None]], -1).astype(np.float32)
# vineta + abajo mas profundo (lugar para el titular)
r2 = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.75)) ** 2
va = np.clip((r2 - 0.3) * 0.7, 0, 0.45) + np.clip((yy - 0.72 * H) / (0.28 * H), 0, 1) * 0.35 * (yy > wave)
L_vig = np.concatenate([np.zeros((H, W, 3)) + np.array([0.0, 0.05, 0.07]), va[..., None]], -1).astype(np.float32)
layers = [('01 Bajo el agua (render 3D)', L_und, 'normal'), ('02 Arriba del agua (render 3D)', L_air, 'normal'),
          ('03 Borde del menisco', L_edge, 'normal'), ('04 Brillo de la superficie', L_surf, 'screen'), ('05 Rayos de sol en el agua', L_rays, 'screen'), ('06 Vineta y profundidad', L_vig, 'normal')]
comp = np.zeros((H, W, 3), np.float32)
for _, Ly, mode in layers:
    a = Ly[..., 3:4]; c = Ly[..., :3]
    comp = comp * (1 - a) + ((1 - (1 - comp) * (1 - c)) if mode == 'screen' else c) * a
Image.fromarray((np.clip(comp, 0, 1) * 255).astype(np.uint8)).save(OUT + '.jpg', quality=93)
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
print('OK')
