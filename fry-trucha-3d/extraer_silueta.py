# Lee el SVG exportado del .ai del icono (pdftocairo -svg icono.ai icono.svg) y guarda cada forma como poligonos
# (subtrazos muestreados de las curvas Bezier) en JSON, en coordenadas del artboard (y hacia abajo).
# python extraer_silueta.py icono.svg salida.json
import sys, re, json
src = open(sys.argv[1]).read()
shapes = []
for d in re.findall(r'<path[^>]* d="([^"]+)"', src):
    tok = re.findall(r'[MCLZ]|-?[\d.]+', d); i = 0; subs = []; cur = []; p = None
    while i < len(tok):
        t = tok[i]; i += 1
        if t == 'M':
            if cur: subs.append(cur)
            p = (float(tok[i]), float(tok[i + 1])); i += 2; cur = [p]
        elif t == 'L':
            p = (float(tok[i]), float(tok[i + 1])); i += 2; cur.append(p)
        elif t == 'C':
            c1 = (float(tok[i]), float(tok[i + 1])); c2 = (float(tok[i + 2]), float(tok[i + 3])); e = (float(tok[i + 4]), float(tok[i + 5])); i += 6
            for k in range(1, 9):
                u = k / 8; v = 1 - u
                cur.append(tuple(v ** 3 * p[j] + 3 * v * v * u * c1[j] + 3 * v * u * u * c2[j] + u ** 3 * e[j] for j in range(2)))
            p = e
        elif t == 'Z':
            if cur: subs.append(cur); cur = []
    if cur: subs.append(cur)
    xs = [q[0] for s in subs for q in s]; ys = [q[1] for s in subs for q in s]
    shapes.append({'bbox': [min(xs), min(ys), max(xs), max(ys)], 'subpaths': subs})
json.dump(shapes, open(sys.argv[2], 'w'))
for k, s in enumerate(shapes): print(k, [round(v) for v in s['bbox']], len(s['subpaths']), [len(x) for x in s['subpaths']])
