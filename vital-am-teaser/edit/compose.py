# Animatic edit for the Vital AM teaser (direction 1): S1 clock (AE-style motion graphics) +
# S2/S3 previs from Blender, with on-screen text, VO subtitles and alarm SFX.
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H, FPS = 1280, 720, 24
PREVIS = sys.argv[1]; OUT = sys.argv[2]
B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
NAVY, CYAN, GOLD, WHITE = (36, 64, 124), (128, 213, 235), (226, 196, 40), (255, 255, 255)
os.makedirs('pv', exist_ok=True); os.makedirs('out', exist_ok=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', PREVIS,
                '-vf', f'scale={W}:{H}:flags=lanczos,eq=contrast=1.04:saturation=1.08',
                'pv/p%04d.png'], check=True)
pv = sorted(os.listdir('pv'))

def font(path, size): return ImageFont.truetype(path, size)
def ease(t): t = max(0.0, min(1.0, t)); return t*t*(3-2*t)
def fade(t, a, b, fin=0.35, fout=0.35):
    if t < a or t > b: return 0.0
    return min(ease((t-a)/fin), ease((b-t)/fout))

def text_layer(lines, y, alpha, glow=False, cx=W/2):
    """lines: [(text, fontpath, size, color, tracking)] centred, stacked from y."""
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    yy = y
    for txt, fp, size, col, track in lines:
        f = font(fp, size)
        widths = [d.textlength(ch, font=f) for ch in txt]; tw = sum(widths) + track*(len(txt)-1)
        x = cx - tw/2
        for ch, cw in zip(txt, widths):
            d.text((x, yy), ch, font=f, fill=(*col, int(255*alpha))); x += cw + track
        yy += int(size*1.35)
    if glow:
        g = L.filter(ImageFilter.GaussianBlur(10)); L = Image.alpha_composite(g, L)
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); shadow.putalpha(L.getchannel('A').filter(ImageFilter.GaussianBlur(6)).point(lambda v: v*0.55))
    return Image.alpha_composite(shadow, L)

def subtitle(vn, en, alpha):
    return text_layer([(vn, R, 26, WHITE, 0), (en, R, 20, (225, 225, 225), 0)], H-118, alpha)

def clock_frame(i):
    t = i/FPS
    im = Image.new('RGB', (W, H), (0, 0, 0))
    a = ease(t/0.5)                                  # clock fades in
    sc = 1.0 + 0.06*ease(t/2.0)                      # slow push-in
    cx, cy, r = W/2, H/2 - 20, 150*sc
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(255, 255, 255, int(235*a)), width=int(6*sc))
    for k in range(12):
        ang = math.radians(k*30); r1 = r*(0.80 if k % 3 == 0 else 0.86)
        d.line((cx+r1*math.sin(ang), cy-r1*math.cos(ang), cx+r*0.92*math.sin(ang), cy-r*0.92*math.cos(ang)),
               fill=(255, 255, 255, int(220*a)), width=int((6 if k % 3 == 0 else 3)*sc))
    m = 20 + 10*ease(t/1.2)                          # minutes sweep 6:20 -> 6:30
    hang = math.radians((6 + m/60)*30); mang = math.radians(m*6)
    d.line((cx, cy, cx+r*0.48*math.sin(hang), cy-r*0.48*math.cos(hang)), fill=(255, 255, 255, int(255*a)), width=int(10*sc))
    d.line((cx, cy, cx+r*0.78*math.sin(mang), cy-r*0.78*math.cos(mang)), fill=(*GOLD, int(255*a)), width=int(6*sc))
    d.ellipse((cx-9, cy-9, cx+9, cy+9), fill=(*GOLD, int(255*a)))
    ring = 1.0 if (0.55 < t < 0.75 or 0.95 < t < 1.15) else 0.0   # alarm "beep beep" pulses
    if ring:
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.ellipse((cx-r*1.15, cy-r*1.15, cx+r*1.15, cy+r*1.15), outline=(*GOLD, 160), width=10)
        L = Image.alpha_composite(g.filter(ImageFilter.GaussianBlur(8)), L)
    L = Image.alpha_composite(L, text_layer([('6:30 AM', B, 34, WHITE, 4)], int(cy + r + 30), a))
    L = Image.alpha_composite(L, subtitle('Một ngày năng lượng bắt đầu từ bữa sáng dinh dưỡng.', 'A great day starts with a healthy breakfast.', fade(t, 0.3, 2.0, 0.3, 0.15)))
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')

N = 48 + len(pv)
for i in range(N):
    t = i/FPS
    if i < 48:
        fr = clock_frame(i)
    else:
        fr = Image.open('pv/' + pv[i-48]).convert('RGBA')
        if i < 52:                                   # quick light flash on the cut from black
            fr = Image.blend(Image.new('RGBA', (W, H), (255, 236, 200, 255)), fr, ease((i-48)/4))
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        L = Image.alpha_composite(L, text_layer([('MỖI BUỔI SÁNG ĐỀU QUAN TRỌNG', B, 40, WHITE, 3), ('EVERY MORNING MATTERS', B, 24, CYAN, 6)], 70, fade(t, 3.2, 5.9, 0.4, 0.3)))
        L = Image.alpha_composite(L, subtitle('Và tôm của bạn cần điều đó.', 'Your shrimp deserve one too.', fade(t, 2.4, 5.6, 0.3, 0.3)))
        a_end = fade(t, 8.4, 10.5, 0.6, 0.1)
        if a_end:
            vign = Image.new('RGBA', (W, H), (10, 18, 40, int(110*a_end)))
            L = Image.alpha_composite(L, vign)
            L = Image.alpha_composite(L, text_layer([('SmartCare', R, 40, WHITE, 1), ('VITAL AM', B, 72, CYAN, 3)], 250, a_end, glow=True, cx=300))
            L = Image.alpha_composite(L, text_layer([('SẮP RA MẮT', B, 30, GOLD, 8), ('COMING SOON', R, 18, WHITE, 6)], 440, fade(t, 8.9, 10.5, 0.5, 0.1), cx=300))
        fr = Image.alpha_composite(fr, L).convert('RGB')
    fr.save(f'out/o{i:04d}.jpg', quality=93)
# alarm SFX: two short beeps at 0.55 s and 0.95 s, silence after
beep = "0.35*sin(2*PI*1760*t)*(between(t,0.55,0.75)+between(t,0.95,1.15))"
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', 'out/o%04d.jpg',
                '-f', 'lavfi', '-i', f"aevalsrc='{beep}':s=48000:d={N/FPS}",
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', OUT], check=True)
print('frames', N, 'duration', N/FPS)
