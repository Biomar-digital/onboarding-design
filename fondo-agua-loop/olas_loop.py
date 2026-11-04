# Loop de olas suaves sobre una imagen fija: desplazamiento vertical ondulante (mas fuerte abajo, en el agua),
# todo periodico en T, asi el ultimo cuadro empalma con el primero. Uso: python3 olas_loop.py in.jpg out.mp4
import sys, subprocess, numpy as np, math
from scipy.ndimage import map_coordinates
src, out = sys.argv[1], sys.argv[2]
T, FPS = float(sys.argv[3]) if len(sys.argv) > 3 else 12.0, 30
W, H = map(int, subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',src]).decode().strip().split(','))
img = np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',src,'-f','rawvideo','-pix_fmt','rgb48le','-']), np.uint16).reshape(H, W, 3).astype(np.float32) / 65535
W2, H2 = W - W % 2, H - H % 2
y, x = np.mgrid[0:H, 0:W].astype(np.float32)
u, v = x / W, y / H
depth = np.clip((v - 0.30) / 0.55, 0, 1) ** 1.2            # 0 arriba (cielo/superficie), 1 abajo
amp = 1.5 + 9.0 * depth                                    # px de ondulacion vertical
# (ciclos a lo ancho, ciclos por loop, amplitud relativa, fase); ciclos por loop enteros = loop perfecto
WAVES = [(0.6, 1, 1.00, 0.3), (1.3, -2, 0.55, 1.9), (2.1, 3, 0.30, 4.1), (0.9, -1, 0.45, 2.7)]
FR = int(round(T * FPS))
enc = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W2}x{H2}','-r',str(FPS),'-i','-',
                        '-c:v','libx264','-preset','slow','-crf','12','-pix_fmt','yuv420p','-movflags','+faststart',out], stdin=subprocess.PIPE)
rng = np.random.default_rng(1)
for f in range(FR):
    t = f / FR
    dy = np.zeros((H, W), np.float32); dx = np.zeros((H, W), np.float32)
    for k, n, a, p in WAVES:
        ph = 2 * math.pi * (k * u + n * t) + p + 2.0 * v * (1 + k)   # las crestas se inclinan un poco con la profundidad
        dy += a * np.sin(ph); dx += 0.35 * a * np.cos(ph + 0.8)
    dy *= amp; dx *= amp * 1.5
    shim = 1 + 0.012 * depth * np.sin(2 * math.pi * (1.7 * u + 2 * t) + 5 * v)   # brillo muy sutil que acompana la ola
    fr = np.stack([map_coordinates(img[..., c], [y + dy, x + dx], order=3, mode='reflect') for c in range(3)], -1) * shim[..., None]
    fr = fr[:H2, :W2] * 255 + rng.uniform(-0.5, 0.5, (H2, W2, 1))   # dither: sin escalones en el degradado
    enc.stdin.write(np.clip(fr + 0.5, 0, 255).astype(np.uint8).tobytes())
    if f % 60 == 0: print('cuadro', f, 'de', FR, flush=True)
enc.stdin.close(); enc.wait(); print('LISTO', out)
