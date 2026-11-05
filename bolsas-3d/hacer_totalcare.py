# Bolsa SmartCare TOTALCARE a partir del 3D de SmartCare ASSIST SKIN: misma malla y UV, texturas recoloreadas
# (naranja -> turquesa, crema -> celeste) y el nombre del producto reemplazado por TOTALCARE en verde.
# python3 hacer_totalcare.py assist.glb salida.glb carpeta_tmp fuente.otf
import json, struct, sys, subprocess, numpy as np, os
SRC, OUT, TMP, FONT = sys.argv[1:5]
os.makedirs(TMP, exist_ok=True)
raw = open(SRC, 'rb').read(); jl = struct.unpack('<I', raw[12:16])[0]; J = json.loads(raw[20:20 + jl]); BIN = raw[20 + jl + 8:]
def view(i): bv = J['bufferViews'][i]; o = bv.get('byteOffset', 0); return BIN[o:o + bv['byteLength']]
def dec(b, name):
    p = os.path.join(TMP, name + '.jpg'); open(p, 'wb').write(b)
    return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']), np.uint8).reshape(2048, 2048, 3).astype(float)
def enc(a, name):
    p = os.path.join(TMP, name + '_tc.jpg')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '2048x2048', '-i', '-', '-q:v', '2', p], input=np.clip(a, 0, 255).astype(np.uint8).tobytes(), check=True)
    return open(p, 'rb').read()
TEAL = np.array([36, 140, 168.0])                               # turquesa medio de la bolsa TotalCare
def recolor(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    L = 0.299 * r + 0.587 * g + 0.114 * b
    w = np.clip((r - b - 45) / 70, 0, 1)[..., None]               # cuanto "naranja" tiene el pixel
    k = (L / 112.0)[..., None]
    kk = np.clip(k, 0, 1); hi = np.clip((k - 1) / 0.8, 0, 1)
    teal = TEAL * kk * (1 - hi) + (TEAL + (255 - TEAL) * 0.75) * hi   # zonas claras/brillos: turquesa claro, sin cian saturado
    out = a * (1 - w) + teal * w
    cream = (np.clip((L - 175) / 30, 0, 1) * np.clip(1 - np.abs(r - b - 15) / 25, 0, 1) * (1 - w[..., 0]))[..., None]
    out = out + cream * np.array([-12, 14, 26.0])                 # crema -> celeste palido
    return out
imgs = {}
for im in J['images']: imgs[im['name']] = dec(view(im['bufferView']), im['name'])
front = imgs['frente_original'].copy()
navy = (front[..., 2] - front[..., 0] > 40) & (front[..., 0] < 120)   # SmartCare en azul marino (antes de recolorear)
# 1) borrar ASSIST SKIN (interpolando el fondo de la etiqueta por columna) y guardar el sombreado de la tela
X0, X1, Y0, Y1 = 748, 1326, 710, 810
top = front[Y0:Y0 + 3, X0:X1].mean(0); bot = front[Y1:Y1 + 3, X0:X1].mean(0)
t = np.linspace(0, 1, Y1 - Y0)[:, None, None]
front[Y0:Y1, X0:X1] = top[None] * (1 - t) + bot[None] * t
shade = front[..., :].mean(-1) / np.median(front[600:900, 800:1300].mean(-1))
# 2) recolorear (ondas y etiqueta)
# dorso: debajo de la etiqueta habia una franja lisa (sin olas); se rellena con las olas de mas abajo, conservando
# el sombreado/pliegues de esa franja, con una transicion suave arriba y abajo
back = imgs['dorso_original'].copy()
B0, B1, SH = 1122, 1345, 290
band = back[B0:B1]; src = back[B0 + SH:B1 + SH]
Lb = band.mean(-1); kern = np.ones(61) / 61
Ls = np.apply_along_axis(lambda r: np.convolve(r, kern, 'same'), 1, Lb)
shade_b = np.clip(Lb / np.maximum(Ls, 1), 0.85, 1.15)[..., None]
srcn = src * (band.mean((0, 1)) / np.maximum(src.mean((0, 1)), 1))          # mismo tono medio que la franja
inside = ((band.max(-1) > 40) & (src.max(-1) > 40))[..., None]
ramp = np.clip(np.minimum(np.arange(B1 - B0), (B1 - B0 - 1) - np.arange(B1 - B0)) / 25.0, 0, 1)[:, None, None]
back[B0:B1] = np.where(inside, band * (1 - ramp) + srcn * shade_b * ramp, band)
front = recolor(front); back = recolor(back)
# 3) TOTALCARE en verde, alineado con SmartCare y un poco mas ancho (como la bolsa real)
xs = np.where(navy[600:700, 600:1500].any(0))[0] + 600
sx0, sx1 = xs.min(), xs.max(); target_h = 77.0                                          # alto de mayuscula del nombre original (ASSIST SKIN)
def text_mask(size):
    p = os.path.join(TMP, 'txt.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=2048x2048', '-frames:v', '1', '-vf',
                    "drawtext=fontfile=%s:text=TOTALCARE:fontcolor=white:fontsize=%d:x=%d:y=%d" % (FONT, size, sx0 - 4, 718), p], check=True)
    m = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 'rawvideo', '-pix_fmt', 'gray', '-']), np.uint8).reshape(2048, 2048) / 255.0
    return m
size = 110
for _ in range(6):                                              # ajustar tamano al ancho buscado
    m = text_mask(size); rws = np.where(m.any(1))[0]; size = int(round(size * target_h / (rws.max() - rws.min() + 1)))
m = text_mask(size); rows = np.where(m.any(1))[0]
print('SmartCare x %d-%d, TOTALCARE size %d, x %d-%d, y %d-%d' % (sx0, sx1, size, np.where(m.any(0))[0].min(), np.where(m.any(0))[0].max(), rows.min(), rows.max()))
GREEN = np.array([108, 168, 46.0])
front = front * (1 - m[..., None]) + (GREEN * np.clip(shade, 0.75, 1.1)[..., None]) * m[..., None]
# 4) reemplazar las imagenes dentro del glb (mismo orden de bufferViews; se reconstruye el buffer binario)
newimg = {}
for im in J['images']: newimg[im['bufferView']] = enc(front if im['name'] == 'frente_original' else back, im['name'])
for im in J['images']: im['name'] = im['name'].replace('original', 'totalcare')
for mt in J['materials']: mt['name'] = mt['name'].replace('original', 'TotalCare')
J['meshes'][0]['name'] = 'Bolsa SmartCare TotalCare'
out = b''
for i, bv in enumerate(J['bufferViews']):
    data = newimg.get(i, view(i))
    while len(out) % 4: out += b'\0'
    bv['byteOffset'] = len(out); bv['byteLength'] = len(data); out += data
while len(out) % 4: out += b'\0'
J['buffers'][0]['byteLength'] = len(out)
js = json.dumps(J, separators=(',', ':')).encode()
while len(js) % 4: js += b' '
glb = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(out)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(out), 0x004E4942) + out
open(OUT, 'wb').write(glb); print('GLB', OUT, len(glb))
