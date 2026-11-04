# Calm, readable schools: every fish keeps a fixed place in its school and the school glides along its
# route at constant speed. No darting, no splitting, no turning back: the only motion off the route is a
# slow, small sway (a few cm), periodic over the loop so frame F joins frame 0 seamlessly.
import numpy as np, math

def slots(NS, half, rng, gap=(0.62, 0.45, 0.38)):
    # NS places inside an ellipsoid (along, depth, height half-sizes), at least one body apart (scaled metric)
    ha = np.maximum(np.array(half, float), 1e-3); g = np.array(gap)
    pts = []
    for scale in (1.0, 0.85, 0.7, 0.55, 0.4):
        tries = 0
        while len(pts) < NS and tries < 40000:
            tries += 1
            q = rng.uniform(-1, 1, 3)
            if (q * q).sum() > 1: continue
            p = q * ha
            if all((((p - o) / (g * scale)) ** 2).sum() >= 1 for o in pts): pts.append(p)
        if len(pts) >= NS: break
    while len(pts) < NS: pts.append(rng.uniform(-1, 1, 3) * ha * 0.5)
    return np.array(pts[:NS])

def formation(lead, F, NS, V, seed=5, half=(3.0, 0.5, 0.5), loop=90.0, fps=24, sway=(0.10, 0.07, 0.05)):
    rng = np.random.default_rng(seed)
    S = slots(NS, half, rng)
    t = np.arange(F) / fps
    P = np.zeros((F, NS, 3))
    k = rng.integers(9, 23, (NS, 3, 2)); ph = rng.uniform(0, 2 * math.pi, (NS, 3, 2))
    w = 2 * math.pi * k / loop                                   # whole cycles per loop: seamless
    for i in range(NS):
        a, b, c = S[i]
        for f in range(F):
            p, d = lead(t[f] + a / max(V, 1e-6))                 # fish further ahead = same path, a bit later
            h = np.array([d[0], d[1], 0.0]); n_ = np.linalg.norm(h); h = h / n_ if n_ > 1e-9 else np.array([1.0, 0, 0])
            side = np.array([-h[1], h[0], 0.0])
            P[f, i] = p + side * b + np.array([0, 0, c])
        sw = np.stack([(np.sin(w[i, ax][:, None] * t[None, :] + ph[i, ax][:, None]).sum(0) * 0.5) for ax in range(3)], -1)   # (F,3)
        # sway in the school frame: along = heading, depth = side, height = up (heading taken from the path)
        dP = np.roll(P[:, i], -1, 0) - np.roll(P[:, i], 1, 0)
        hh = dP.copy(); hh[:, 2] = 0; hh /= np.maximum(np.linalg.norm(hh, axis=1, keepdims=True), 1e-9)
        sd = np.stack([-hh[:, 1], hh[:, 0], np.zeros(F)], -1)
        P[:, i] += hh * (sw[:, 0:1] * sway[0]) + sd * (sw[:, 1:2] * sway[1]) + np.array([0, 0, 1.0]) * (sw[:, 2:3] * sway[2])
    Vt = (np.roll(P, -1, 0) - np.roll(P, 1, 0)) * fps * 0.5
    # straight lanes wrap (fish re-enter at the far end, off-screen): keep the heading of the neighbouring frame
    jump = np.linalg.norm(Vt, axis=-1) > 3 * max(V, 0.3) + 2.0
    for _ in range(3): Vt = np.where(jump[..., None], np.roll(Vt, 1, 0), Vt); jump = np.linalg.norm(Vt, axis=-1) > 3 * max(V, 0.3) + 2.0
    return P, Vt
