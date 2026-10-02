# Builds the chunky 10 kg Vital AM bag GLB from the SmartCare mockup mesh:
# deforms the mesh (wider, shorter, much fuller body, flat top seal), recomputes
# normals and maps the Vital AM art so it stays undistorted on the new shape.
import json, struct, sys
import numpy as np
from PIL import Image
SRC, ART, TEXSHADE, OUT, FLIPBACK = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] == '1'
SX, SY, SZ = 1.20, 0.90, 1.90          # width, height, fullness
b = open(SRC, 'rb').read(); l = struct.unpack('<I', b[12:16])[0]
j = json.loads(b[20:20+l]); binb = bytearray(b[20+l+8:])
def view(ai):
    a = j['accessors'][ai]; bv = j['bufferViews'][a['bufferView']]
    n = {'VEC2': 2, 'VEC3': 3, 'SCALAR': 1}[a['type']]
    dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32}[a['componentType']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(binb, dt, a['count']*n, off).reshape(-1, n) if n > 1 else np.frombuffer(binb, dt, a['count'], off), off
def smooth(e0, e1, x):
    t = np.clip((x-e0)/(e1-e0), 0, 1); return t*t*(3-2*t)
for p in j['meshes'][0]['primitives']:
    P, poff = view(p['attributes']['POSITION']); P = P.copy()
    y0, y1 = 0.0073, 0.731; t = (P[:, 1]-y0)/(y1-y0)
    f = smooth(-0.02, 0.06, t) * (1 - smooth(0.80, 0.95, t))      # fullness profile: flat seal on top
    P[:, 2] *= 1 + (SZ-1)*f
    P[:, 0] *= SX * (1 + 0.05*f)
    P[:, 1] = y0 + (P[:, 1]-y0)*SY
    I, _ = view(p['indices']); I = I.reshape(-1, 3).astype(np.int64)
    fn = np.cross(P[I[:, 1]]-P[I[:, 0]], P[I[:, 2]]-P[I[:, 0]])
    Nold, noff = view(p['attributes']['NORMAL'])
    N = np.zeros_like(P); [np.add.at(N, I[:, k], fn) for k in range(3)]
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    if (N*Nold).sum(1).mean() < 0: N = -N
    binb[poff:poff+P.nbytes] = P.astype(np.float32).tobytes()
    binb[noff:noff+N.nbytes] = N.astype(np.float32).tobytes()
    a = j['accessors'][p['attributes']['POSITION']]; a['min'] = P.min(0).tolist(); a['max'] = P.max(0).tolist()
# --- texture: art undistorted on the new face (UV rect -> metres)
u0, u1, v0, v1 = 600, 1467, 254, 1735
faceW, faceH = 0.41*SX*1.03, 0.724*SY
pxm_x, pxm_y = (u1-u0)/faceW, (v1-v0)/faceH
art = Image.open(ART).convert('RGB').crop((335, 0, 2107, 2560))
seal_m, bottom_m = 0.035, 0.012
artH_m = faceH - seal_m - bottom_m                          # whole design fits the height ("10 Kg" stays visible)
artW_m = min(faceW, artH_m*1772/2560*1.07)                  # at most 7% horizontal stretch
aw, ah = round(artW_m*pxm_x), round(artH_m*pxm_y)
art = art.resize((aw, ah), Image.LANCZOS)
canvas = Image.new('RGB', (2048, 2048), (38, 67, 125))
ax0 = u0 + ((u1-u0)-aw)//2; ay0 = v0 + round(seal_m*pxm_y)
canvas.paste(art, (ax0, ay0))
a = np.asarray(canvas).astype(np.float32)
a[:, :ax0] = a[:, ax0:ax0+1]; a[:, ax0+aw:] = a[:, ax0+aw-1:ax0+aw]   # extend art sideways
a[ay0+ah:, :] = a[ay0+ah-1:ay0+ah, :]                                    # and below
canvas = Image.fromarray(a.astype(np.uint8))
print('art on bag (m):', round(artW_m, 3), 'x', round(artH_m, 3), 'face', round(faceW, 3), 'x', round(faceH, 3))
c = np.asarray(canvas).astype(np.float32)/255
c[:, :u0] = c[:, u0:u0+1]; c[:, u1:] = c[:, u1-1:u1]; c[v1:, :] = c[v1-1:v1, :]
# side seams: per texture row, find where the mesh outline sits in UV space and blend
# both outline edges to the same colour so front and back meet cleanly at the sides
p0 = j['meshes'][0]['primitives'][0]
UV, _ = view(p0['attributes']['TEXCOORD_0'])
px = UV[:, 0]*2048; py = UV[:, 1]*2048
rows = np.clip(py.astype(int), 0, 2047)
uL = np.full(2048, np.nan); uR = np.full(2048, np.nan)
np.fmin.at(uL, rows, px); np.fmax.at(uR, rows, px)
ok = ~np.isnan(uL); idx = np.arange(2048)
uL = np.interp(idx, idx[ok], uL[ok]); uR = np.interp(idx, idx[ok], uR[ok])
bw = 60
for yy in range(2048):
    a, bR = int(uL[yy]), int(uR[yy])
    target = 0.5*(c[yy, min(a+2, 2047)] + c[yy, max(bR-2, 0)])
    for k in range(bw):
        wgt = (1 - k/bw)**2
        if a+k < 2048: c[yy, a+k] = c[yy, a+k]*(1-wgt) + target*wgt
        if bR-k >= 0: c[yy, bR-k] = c[yy, bR-k]*(1-wgt) + target*wgt
    c[yy, :max(a, 0)] = target; c[yy, min(bR+1, 2048):] = target
D = np.asarray(Image.open(TEXSHADE).convert('L')).astype(np.float32)/255*1.25
front = np.clip(c*D[..., None], 0, 1)
back = front.copy()
if FLIPBACK: back[:, u0:u1] = front[:, u0:u1][:, ::-1]
imgs = []
for arr in (front, back):
    import io; buf = io.BytesIO(); Image.fromarray((arr*255).astype(np.uint8)).save(buf, 'JPEG', quality=92); imgs.append(buf.getvalue())
Image.fromarray((front*255).astype(np.uint8)).save('vital_front_10kg.jpg', quality=92)
repl = {j['images'][0]['bufferView']: imgs[0], j['images'][1]['bufferView']: imgs[1]}
out = bytearray()
for i, bv in enumerate(j['bufferViews']):
    data = repl.get(i, bytes(binb[bv.get('byteOffset', 0):bv.get('byteOffset', 0)+bv['byteLength']]))
    while len(out) % 4: out += b'\0'
    bv['byteOffset'] = len(out); bv['byteLength'] = len(data); out += data
while len(out) % 4: out += b'\0'
j['buffers'][0]['byteLength'] = len(out)
j['images'][0]['name'] = 'vital_am_frente'; j['images'][1]['name'] = 'vital_am_dorso'
j['materials'][0]['name'] = 'Frente — Vital AM'; j['materials'][1]['name'] = 'Dorso — Vital AM'
j['nodes'][0]['name'] = 'SmartCare Vital AM — bolsa 10kg'
js = json.dumps(j, separators=(',', ':')).encode()
while len(js) % 4: js += b' '
open(OUT, 'wb').write(struct.pack('<III', 0x46546C67, 2, 28+len(js)+len(out)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(out), 0x004E4942) + bytes(out))
print('bounds', [round(v, 3) for v in j['accessors'][0]['min']], [round(v, 3) for v in j['accessors'][0]['max']])
