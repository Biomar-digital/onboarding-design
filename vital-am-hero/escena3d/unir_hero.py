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
wave = wl + 2.0 * k * np.sin(xx / (60 * k)) + 1.0 * k * np.sin(xx / (17 * k) + 1.1)
m = np.clip((yy - wave) / (2 * k) + 0.5, 0, 1)
L_air = np.concatenate([air, (1 - m)[..., None]], -1)
L_und = np.concatenate([und, np.ones((H, W, 1), np.float32)], -1)
# brillo de la superficie: linea fina + reflejo suave por debajo
band = np.exp(-((yy - wave) / (2.2 * k)) ** 2) * 0.55 + np.exp(-((yy - wave - 10 * k) / (8 * k)) ** 2) * (yy > wave) * 0.18
L_surf = np.concatenate([np.ones((H, W, 3)) * np.array([1.0, 0.95, 0.86]), band[..., None]], -1).astype(np.float32)
# rayos de sol que siguen bajo el agua desde el sol (busca el punto mas brillante del cielo)
sky = air[: int(wl) - 2].mean(-1); skyb = np.asarray(Image.fromarray((sky * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(20 * k)))
sy, sx = np.unravel_index(np.argmax(skyb), sky.shape)
ang = np.arctan2(xx - sx, yy - sy); rng = np.random.default_rng(3); st = np.zeros_like(ang)
for _ in range(10): st += np.maximum(np.sin(ang * rng.uniform(25, 80) + rng.uniform(0, 6.28)), 0) ** rng.uniform(3, 8) * rng.uniform(0.3, 1)
st /= st.max(); fall = np.clip(1 - (yy - wl) / (0.55 * H), 0, 1) ** 1.5 * (yy > wave + 4 * k) * np.exp(-(ang / 0.6) ** 2)
ray_a = np.asarray(Image.fromarray((np.clip(st * fall * 0.35, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5 * k)), np.float32) / 255
L_rays = np.concatenate([np.ones((H, W, 3)) * np.array([1.0, 0.93, 0.76]), ray_a[..., None]], -1).astype(np.float32)
# vineta + abajo mas profundo (lugar para el titular)
r2 = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.75)) ** 2
va = np.clip((r2 - 0.3) * 0.7, 0, 0.45) + np.clip((yy - 0.72 * H) / (0.28 * H), 0, 1) * 0.35 * (yy > wave)
L_vig = np.concatenate([np.zeros((H, W, 3)) + np.array([0.0, 0.05, 0.07]), va[..., None]], -1).astype(np.float32)
layers = [('01 Bajo el agua (render 3D)', L_und, 'normal'), ('02 Arriba del agua (render 3D)', L_air, 'normal'),
          ('03 Superficie del agua', L_surf, 'screen'), ('04 Rayos de sol en el agua', L_rays, 'screen'), ('05 Vineta y profundidad', L_vig, 'normal')]
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
