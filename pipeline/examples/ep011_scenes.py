# ---------------- scene drawing ----------------
def wave_path(cx, cy, width, amp, t, n=220, sweep=True, phase=0):
    pts = []
    for i in range(n):
        u = i / (n - 1); x = cx - width / 2 + u * width
        env = math.sin(math.pi * u) ** 1.5
        f = 6 + (18 * u if sweep else 0)
        y = cy - amp * env * math.sin(2 * math.pi * (f * u) - t * 6 + phase)
        pts.append((x, y))
    return pts

def s_hook(t, arr, img):
    # abyss with a glowing waveform rising out of the dark
    arr[:] = grad((6, 22, 34), (0, 3, 8), 0.8)
    arr += RAYS[..., None] * np.array([40, 90, 110], np.float32) * 0.55
    snow(arr, t, 0.04)
    rise = 1060 - 180 * eout(t / 2.2)
    amp = 150 + 60 * math.sin(t * 2.1)
    pts = wave_path(W / 2, rise, 900, amp, t)
    g = glow_img(lambda d, s: d.line([(x * s, y * s) for x, y in pts], fill=(60, 200, 255), width=max(1, int(40 * s))), 40)
    arr[:] = screen(arr, g * 1.2)
    sh = sharp_img(lambda d, s: d.line(pts, fill=(200, 250, 255), width=7))
    arr[:] = screen(arr, sh)
    return [lambda: label(img, t, 0.0, "THE BLOOP: SOLVED", 270, 120, (120, 255, 150), "NOAA: IT WAS ICE CRACKING", (120, 255, 150), t1=ps(1) - 0.05),
            lambda: label(img, t, ps(1), "THIS SOUND", 270, 130, WHITE, None),
            lambda: label(img, t, ps(2), "NEVER SOLVED", 430, 140, RED, None)]

def submarine(d, s, x, y, L, col):
    h = L * 0.13
    d.rounded_rectangle(((x - L / 2) * s, (y - h / 2) * s, (x + L / 2) * s, (y + h / 2) * s), radius=h / 2 * s, fill=col)
    d.polygon([((x + L * 0.05) * s, (y - h / 2) * s), ((x + L * 0.08) * s, (y - h * 1.35) * s), ((x + L * 0.2) * s, (y - h * 1.35) * s), ((x + L * 0.23) * s, (y - h / 2) * s)], fill=col)
    d.polygon([((x - L / 2 + 10) * s, y * s), ((x - L / 2 - L * 0.06) * s, (y - h * 0.8) * s), ((x - L / 2 - L * 0.06) * s, (y + h * 0.8) * s)], fill=col)

def s_navy(t, arr, img, t0):
    lt = t - t0
    arr[:] = grad((40, 110, 135), (2, 10, 16), 0.75)
    arr += RAYS[..., None] * np.array([90, 160, 180], np.float32) * 0.8
    arr[:] = screen(arr, glow_img(lambda d, s: d.ellipse((140 * s, 380 * s, 940 * s, 900 * s), fill=(40, 110, 130)), 160))
    snow(arr, t, 0.05)
    # submarine passing overhead
    sx = -420 + lt * 250; sy = 650 + 15 * math.sin(lt)
    sub = sharp_img(lambda d, s: submarine(d, s, sx, sy, 760, (255, 255, 255)))
    arr[:] = arr * (1 - sub / 255 * 0.92)
    rim = glow_img(lambda d, s: submarine(d, s, sx, sy - 6, 760, (40, 80, 90)), 10, 2)
    arr += rim * 0.35
    # seabed
    bed = sharp_img(lambda d, s: d.polygon([(0, 1560), (300, 1530), (640, 1555), (1080, 1520), (1080, 1920), (0, 1920)], fill=(255, 255, 255)))
    arr[:] = arr * (1 - bed / 255) + bed / 255 * np.array([22, 36, 40], np.float32)
    # hydrophone on tripod
    hx, hy = 540, 1470
    def hyd(d, s, c1=(120, 145, 150)):
        d.line([(hx * s, hy * s), ((hx - 80) * s, (hy + 85) * s)], fill=c1, width=int(9 * s) or 1)
        d.line([(hx * s, hy * s), ((hx + 80) * s, (hy + 85) * s)], fill=c1, width=int(9 * s) or 1)
        d.rounded_rectangle(((hx - 34) * s, (hy - 150) * s, (hx + 34) * s, (hy + 10) * s), radius=30 * s, fill=c1)
        d.line([((hx + 80) * s, (hy + 85) * s), (1100 * s, (hy + 60) * s)], fill=(40, 50, 52), width=int(6 * s) or 1)
    tmp = sharp_img(hyd); m = (tmp.sum(2, keepdims=True) > 0)
    arr[:] = np.where(m, tmp, arr)
    blink = 0.5 + 0.5 * math.sin(lt * 6)
    arr[:] = screen(arr, glow_img(lambda d, s: d.ellipse(((hx - 14) * s, (hy - 120) * s, (hx + 14) * s, (hy - 92) * s), fill=(80, 255, 140)), 30) * (0.6 + 0.8 * blink))
    # sonar rings
    def rings(d, s):
        for k in range(4):
            r = ((lt * 260 + k * 300) % 1200)
            a = max(0, 1 - r / 1200)
            d.ellipse(((hx - r) * s, (hy - 120 - r * 0.32) * s, (hx + r) * s, (hy - 120 + r * 0.32) * s), outline=tuple(int(c * a) for c in (90, 230, 255)), width=max(1, int(5 * s)))
    arr[:] = screen(arr, sharp_img(rings) * 0.8)
    arr[:] = screen(arr, glow_img(rings, 12, 2) * 0.8)
    return [lambda: label(img, t, t0 + 0.1, "1991", 250, 150, AMBER, "U.S. NAVY  ·  SOSUS HYDROPHONES"),
            lambda: tag(img, t, ps(4), "▲ UNKNOWN SIGNAL DETECTED", (230, 760), RED, 44)]

def s_spectro(t, arr, img, t0):
    lt = t - t0
    arr[:] = grad((4, 14, 22), (0, 2, 6), 1.0)
    snow(arr, t, 0.03, bright=0.5)
    # panel
    px0, py0, px1, py1 = 90, 590, 990, 1100
    def panel(d, s):
        d.rectangle((px0, py0, px1, py1), outline=(40, 90, 110), width=3)
        for k in range(1, 6):
            y = py0 + k * (py1 - py0) / 6; d.line([(px0, y), (px1, y)], fill=(18, 42, 52), width=2)
        for k in range(1, 10):
            x = px0 + k * (px1 - px0) / 10; d.line([(x, py0), (x, py1)], fill=(18, 42, 52), width=2)
    pl = sharp_img(panel); arr[:] = np.maximum(arr, pl)
    # sweeps: each sweep appears at a time and scrolls left
    times = [ps(5) + 0.1, ps(6) + 0.1, ps(6) + 0.9] + [SOUND_AT + k * 0.66 for k in range(4)]
    scroll = 110
    def sweeps(d, s, w):
        for k, ts in enumerate(times):
            if t < ts: continue
            age = t - ts
            xs = px1 - 120 - age * scroll
            if xs < px0 + 10: continue
            grow = eout(age / 0.5)
            pts = []
            for i in range(30):
                u = i / 29 * grow
                x = xs + u * 70; y = py1 - 60 - u ** 1.6 * (py1 - py0 - 140)
                pts.append((x * s, y * s))
            hot = 1.0 if k >= 3 else 0.7
            d.line(pts, fill=tuple(int(c * hot) for c in (120, 240, 255)), width=max(1, int(w * s)))
    arr[:] = screen(arr, glow_img(lambda d, s: sweeps(d, s, 30), 26) * 1.2)
    arr[:] = screen(arr, sharp_img(lambda d, s: sweeps(d, s, 6)))
    # big audio-reactive waveform under the panel when the sound plays
    e = upenv(t)
    if e > 0.01 or t > SOUND_AT:
        amp = 30 + 230 * e
        pts = wave_path(W / 2, 1300, 960, amp, t * 2.2, 260, True)
        arr[:] = screen(arr, glow_img(lambda d, s: d.line([(x * s, y * s) for x, y in pts], fill=(70, 220, 255), width=max(1, int(36 * s))), 34) * (0.5 + e))
        arr[:] = screen(arr, sharp_img(lambda d, s: d.line(pts, fill=(210, 250, 255), width=6)) * (0.4 + 0.6 * e))
    ax = lambda: (tag(img, t, t0, "FREQUENCY ↑", (px0 + 10, py0 - 50), (120, 170, 185), 30), tag(img, t, t0, "TIME →", (px1 - 130, py1 + 14), (120, 170, 185), 30))
    out = [ax, lambda: label(img, t, t0 + 0.05, "THE UPSWEEP", 260, 130, CYAN, "A RISING WAIL, REPEATING", WHITE)]
    out.append(lambda: tag(img, t, SOUND_AT - 0.3, "SOUND RECREATION  ·  BASED ON NOAA RECORDINGS", (95, 1450), AMBER, 30, SOUND_AT + 3.2))
    return out

def chart_base(arr, t, zoom, cx=540, cy=1000):
    arr[:] = grad((6, 26, 52), (2, 10, 24), 1.0)
    def grid(d, s):
        for k in range(-8, 9):
            y = cy + k * 160 * zoom; d.line([(0, y), (W, y)], fill=(30, 70, 110), width=2)
            x = cx + k * 160 * zoom; d.line([(x, 0), (x, H)], fill=(30, 70, 110), width=2)
    arr[:] = np.maximum(arr, sharp_img(grid))
    # faint wave texture
    arr += (np.sin(xx / 37 + t * 0.8 + np.sin(yy / 53)) * np.sin(yy / 29 - t * 0.6) * 6)[..., None]

def s_pacific(t, arr, img, t0):
    lt = t - t0; zoom = 1.25 - 0.45 * ease(lt / 4)
    chart_base(arr, t, zoom)
    cx, cy = 540, 1000
    def rings(d, s, w):
        for k in range(7):
            r = ((lt * 420 + k * 190) % 1500) * zoom * 1.4
            a = max(0, 1 - r / 1700)
            d.ellipse(((cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s), outline=tuple(int(c * a) for c in (90, 230, 255)), width=max(1, int(w * s)))
    arr[:] = screen(arr, glow_img(lambda d, s: rings(d, s, 22), 16) * 0.9)
    arr[:] = screen(arr, sharp_img(lambda d, s: rings(d, s, 5)))
    arr[:] = screen(arr, glow_img(lambda d, s: d.ellipse(((cx - 30) * s, (cy - 30) * s, (cx + 30) * s, (cy + 30) * s), fill=(150, 240, 255)), 40) * (1 + 0.5 * math.sin(lt * 8)))
    return [lambda: label(img, t, t0 + 0.1, "HEARD ACROSS", 250, 120, WHITE, None),
            lambda: label(img, t, t0 + 0.6, "THE ENTIRE PACIFIC", 400, 120, CYAN, None)]

def s_remote(t, arr, img, t0):
    lt = t - t0; zoom = 0.8 + 0.25 * ease(lt / 6)
    chart_base(arr, t, zoom)
    cx, cy = 540, 1000
    # lat/long labels
    def gl(d, s):
        f = font(FONT_SM, 28)
        for k, lab in [(-1, "50°S"), (0, "54°S"), (1, "60°S")]:
            d.text((20, cy + k * 160 * zoom - 34), lab, font=f, fill=(90, 140, 180))
        for k, lab in [(-1, "160°W"), (0, "140°W"), (1, "120°W")]:
            d.text((cx + k * 160 * zoom + 8, 140), lab, font=f, fill=(90, 140, 180))
    tmp = Image.new("RGB", (W, H), 0); gl(ImageDraw.Draw(tmp), 1); arr[:] = np.maximum(arr, np.asarray(tmp, np.float32))
    # pin drop
    drop = eout((lt - 0.2) / 0.5); py = cy - 400 * (1 - drop)
    pulse = (lt * 1.2) % 1
    def pin(d, s):
        d.ellipse(((cx - 26) * s, (py - 26) * s, (cx + 26) * s, (py + 26) * s), fill=RED)
    if lt > 0.2:
        rr = 40 + pulse * 260
        arr[:] = screen(arr, sharp_img(lambda d, s: d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=tuple(int(c * (1 - pulse)) for c in RED), width=5)))
        arr[:] = screen(arr, glow_img(pin, 50) * 1.5)
        arr[:] = screen(arr, sharp_img(pin))
    # direction arrows to the nearest land
    out = [lambda: label(img, t, t0 + 0.1, "54°S  140°W", 250, 120, RED, "ONE OF THE EMPTIEST PLACES ON EARTH", WHITE),
           lambda: tag(img, t, ps(10), "← NEW ZEALAND", (40, 1440), WHITE, 40),
           lambda: tag(img, t, ps(10) + 0.4, "SOUTH AMERICA →", (650, 1440), WHITE, 40),
           lambda: tag(img, t, ps(10) + 0.9, "~2,500 MILES OF OPEN OCEAN", (230, 1510), AMBER, 40)]
    return out

def whale(d, s, x, y, L, t, col):
    pts_top, pts_bot = [], []
    for i in range(41):
        u = i / 40
        th = L * 0.11 * (math.sin(math.pi * min(1, u * 1.15)) ** 0.7) * (1 - 0.75 * u ** 2.5)
        wob = math.sin(t * 2.2 - u * 3) * L * 0.03 * u ** 2
        px = x + L / 2 - u * L; pts_top.append(((px) * s, (y - th + wob) * s)); pts_bot.append((px * s, (y + th * 0.85 + wob) * s))
    d.polygon(pts_top + pts_bot[::-1], fill=col)
    tx, ty = x - L / 2, y + math.sin(t * 2.2 - 3) * L * 0.03
    flap = math.sin(t * 2.2) * L * 0.05
    d.polygon([((tx + 10) * s, ty * s), ((tx - L * 0.12) * s, (ty - L * 0.08 + flap) * s), ((tx - L * 0.06) * s, ty * s), ((tx - L * 0.12) * s, (ty + L * 0.08 + flap) * s)], fill=col)
    d.polygon([((x + L * 0.2) * s, (y + L * 0.05) * s), ((x + L * 0.05) * s, (y + L * 0.17) * s), ((x + L * 0.12) * s, (y + L * 0.05) * s)], fill=col)

def s_whale(t, arr, img, t0):
    lt = t - t0
    arr[:] = grad((12, 44, 62), (1, 6, 12), 1.0)
    arr += RAYS[..., None] * np.array([50, 110, 130], np.float32) * 0.7
    snow(arr, t, 0.05)
    fade = 1 - ease((t - ps(13)) / 0.6)
    wx = 80 + lt * 150; wy = 820 + 40 * math.sin(lt * 0.8)
    wh = sharp_img(lambda d, s: whale(d, s, wx, wy, 900, lt, (255, 255, 255)))
    arr[:] = arr * (1 - wh / 255 * 0.8 * fade)
    arr += glow_img(lambda d, s: whale(d, s, wx, wy - 5, 900, lt, (30, 70, 80)), 12, 2) * 0.3 * fade
    # comparison: steady signal line
    if t > ps(12):
        k = eout((t - ps(12)) / 0.5)
        pts = [(90 + i * 9, 1430 - 40 * math.sin(i * 0.35 - t * 5) * k) for i in range(101)]
        arr[:] = screen(arr, glow_img(lambda d, s: d.line([(x * s, y * s) for x, y in pts], fill=(70, 220, 255), width=max(1, int(28 * s))), 20) * k)
        arr[:] = screen(arr, sharp_img(lambda d, s: d.line(pts, fill=(210, 250, 255), width=5)) * k)
    if t > ps(13):
        k = eout((t - ps(13)) / 0.25)
        def X(d, s):
            c = 820; r = 260 * (1.3 - 0.3 * k)
            d.line([((540 - r) * s, (c - r) * s), ((540 + r) * s, (c + r) * s)], fill=RED, width=max(1, int(40 * s)))
            d.line([((540 + r) * s, (c - r) * s), ((540 - r) * s, (c + r) * s)], fill=RED, width=max(1, int(40 * s)))
        arr[:] = screen(arr, glow_img(X, 30) * k)
        arr[:] = screen(arr, sharp_img(X) * k)
    return [lambda: label(img, t, t0 + 0.1, "THEORY #1: WHALES?", 260, 110, WHITE, None, t1=ps(13) - 0.1),
            lambda: tag(img, t, ps(12), "TOO STEADY TO BE ALIVE", (250, 1500), CYAN, 40),
            lambda: label(img, t, ps(13), "NOT WHALES", 260, 150, RED, None)]

def s_strange(t, arr, img, t0):
    lt = t - t0
    arr[:] = grad((8, 20, 34), (0, 3, 8), 1.0)
    snow(arr, t, 0.06, bright=0.8)
    season = 0.5 + 0.5 * math.sin(lt * 1.6)
    swell = 0.4 + 0.6 * ease((t - ps(15)) / 2.5) if t > ps(15) else 0.4
    amp = 80 + 260 * swell * (0.7 + 0.3 * season)
    pts = wave_path(W / 2, 980, 980, amp, t * 1.5, 260)
    arr[:] = screen(arr, glow_img(lambda d, s: d.line([(x * s, y * s) for x, y in pts], fill=(80, 200, 255), width=max(1, int(46 * s))), 40) * 1.1)
    arr[:] = screen(arr, sharp_img(lambda d, s: d.line(pts, fill=(220, 250, 255), width=7)))
    out = [lambda: label(img, t, t0 + 0.05, "IT GOT STRANGER", 250, 120, WHITE, None, t1=ps(15) - 0.1)]
    if t > ps(15):
        out.append(lambda: tag(img, t, ps(15) + 0.2, "SPRING  ▲ LOUDER", (120, 1440), (150, 255, 170), 46))
        out.append(lambda: tag(img, t, ps(15) + 1.4, "AUTUMN  ▲ LOUDER", (560 - 20, 1520), AMBER, 46))
        out.append(lambda: label(img, t, ps(15), "EVERY YEAR", 250, 120, WHITE, None, t1=ps(16) - 0.1))
    out.append(lambda: label(img, t, ps(16), "NO ONE KNOWS WHY", 250, 120, RED, None))
    return out

TER = [np.cumsum(rng.normal(0, 1, 400)) for _ in range(3)]
def s_volcano(t, arr, img, t0):
    lt = t - t0; desc = ease(lt / 7)
    arr[:] = grad((10, 24, 34), (40, 8, 4), 1.2)
    # red glow from below
    gx, gy = 540, 1500 - desc * 120
    flick = 0.85 + 0.15 * math.sin(lt * 13) * math.sin(lt * 7.3)
    arr[:] = screen(arr, glow_img(lambda d, s: d.ellipse(((gx - 300) * s, (gy - 120) * s, (gx + 300) * s, (gy + 160) * s), fill=(255, 80, 25)), 120) * (1.1 + 0.6 * desc) * flick)
    # terrain layers (parallax)
    for li, (base, col, par) in enumerate([(1250, (48, 26, 24), 0.4), (1380, (28, 14, 12), 0.7), (1520, (10, 5, 4), 1.0)]):
        nz = TER[li]; nz = (nz - nz.min()) / (np.ptp(nz) + 1e-9)
        yb = base - desc * 260 * par
        pts = [(i * W / 399, yb - nz[i] * 160 * (1 + li * 0.3) - (100 if li == 2 and 180 < i < 220 else 0) * 0) for i in range(400)]
        poly = pts + [(W, H), (0, H)]
        m = sharp_img(lambda d, s: d.polygon(poly, fill=(255, 255, 255)))
        arr[:] = arr * (1 - m / 255) + m / 255 * np.array(col, np.float32)
        arr[:] = screen(arr, glow_img(lambda d, s: d.line([(x * s, y * s) for x, y in pts], fill=(255, 90, 30), width=max(1, int(10 * s))), 10, 2) * (0.5 + 0.25 * li) * flick)
    # fissure glow line
    vy = 1500 - desc * 260
    arr[:] = screen(arr, glow_img(lambda d, s: d.ellipse((440 * s, (vy - 40) * s, 640 * s, (vy + 40) * s), fill=(255, 140, 40)), 50) * 1.4 * flick)
    arr[:] = screen(arr, glow_img(lambda d, s: d.polygon([(500 * s, vy * s), (580 * s, vy * s), (640 * s, (vy - 520) * s), (440 * s, (vy - 520) * s)], fill=(120, 40, 15)), 60) * flick)
    # rising embers / bubbles
    def emb(d, s):
        for k in range(40):
            ph = (lt * 0.25 + k * 0.137) % 1
            x = 540 + math.sin(k * 3.1 + lt) * 260 * ph + (k % 7 - 3) * 20
            y = 1500 - desc * 260 - ph * 1100
            r = 3 + (k % 4)
            d.ellipse(((x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s), fill=tuple(int(c * (1 - ph)) for c in (255, 150, 70)))
    arr[:] = screen(arr, sharp_img(emb))
    return [lambda: label(img, t, t0 + 0.05, "THE BEST GUESS?", 250, 120, WHITE, None, t1=ps(18) - 0.1),
            lambda: label(img, t, ps(18), "A HIDDEN VOLCANO", 250, 130, (255, 120, 50), "INFERRED VOLCANIC ACTIVITY  ·  NOAA", WHITE, t1=ps(19) - 0.1),
            lambda: label(img, t, ps(19), "SOURCE: NEVER FOUND", 250, 130, RED, "ORIGIN STILL UNRESOLVED", WHITE)]

def s_fade(t, arr, img, t0, t_end):
    lt = t - t0; dark = ease((t - ps(22)) / (t_end - ps(22)))
    arr[:] = grad((6, 18, 28), (0, 2, 5), 0.9) * (1 - 0.85 * dark)
    snow(arr, t, 0.02, bright=1 - dark * 0.9)
    shrink = 1 - 0.85 * ease(lt / (t_end - t0))
    pts = wave_path(W / 2, 960, 900, 220 * shrink, t, 220)
    arr[:] = screen(arr, glow_img(lambda d, s: d.line([(x * s, y * s) for x, y in pts], fill=(70, 200, 255), width=max(1, int(36 * s))), 32) * shrink)
    arr[:] = screen(arr, sharp_img(lambda d, s: d.line(pts, fill=(210, 250, 255), width=6)) * (0.3 + 0.7 * shrink))
    # timeline bar 1991 -> today
    def bar(d, s):
        x0, x1, y = 150, 930, 1440
        d.line([(x0, y), (x1, y)], fill=(60, 80, 90), width=6)
        p = ease(lt / 3)
        for i in range(60):
            u = i / 59
            if u > p: break
            x = x0 + u * (x1 - x0); hgt = 60 * (1 - 0.8 * u)
            d.line([(x, y - hgt), (x, y + hgt)], fill=tuple(int(c * (1 - 0.6 * u)) for c in (90, 230, 255)), width=6)
    if t < ps(22):
        arr[:] = screen(arr, sharp_img(bar))
    return [lambda: label(img, t, t0 + 0.05, "SINCE 1991…", 250, 120, WHITE, None, t1=ps(22) - 0.1),
            lambda: tag(img, t, t0 + 0.3, "1991", (130, 1500), CYAN, 36, ps(22)),
            lambda: tag(img, t, t0 + 0.3, "TODAY", (850, 1500), CYAN, 36, ps(22)),
            lambda: label(img, t, ps(21), "IT'S FADING", 420, 110, CYAN, None, t1=ps(22) - 0.1),
            lambda: label(img, t, ps(23), "GOING SILENT", 300, 120, (200, 60, 60), None)]

def s_outro(t, arr, img, t0):
    lt = t - t0
    arr[:] = grad((10, 7, 4), (0, 0, 0), 0.7)
    cx, top = 540, 900
    flick = 1 + 0.06 * math.sin(lt * 17) + 0.04 * math.sin(lt * 7.7)
    arr[:] = screen(arr, glow_img(lambda d, s: d.ellipse(((cx - 360) * s, (top - 380) * s, (cx + 360) * s, (top + 260) * s), fill=(255, 140, 40)), 160) * 0.55 * flick)
    def candle(d, s):
        d.rounded_rectangle(((cx - 70) * s, top * s, (cx + 70) * s, (top + 420) * s), radius=12 * s, fill=(235, 220, 190))
        d.line([(cx * s, (top - 4) * s), (cx * s, (top - 34) * s)], fill=(30, 20, 15), width=max(1, int(5 * s)))
    c = sharp_img(candle); m = c.sum(2, keepdims=True) > 0
    shade = (0.55 + 0.45 * np.clip(1 - np.abs(xx - cx) / 70, 0, 1))[..., None]
    arr[:] = np.where(m, c * shade, arr)
    sway = 6 * math.sin(lt * 3.1)
    def flame(d, s, sc=1.0, col=(255, 200, 90)):
        h = 120 * sc * flick
        d.polygon([((cx - 26 * sc) * s, (top - 40) * s), ((cx + sway) * s, (top - 40 - h) * s), ((cx + 26 * sc) * s, (top - 40) * s)], fill=col)
        d.ellipse(((cx - 26 * sc) * s, (top - 66) * s, (cx + 26 * sc) * s, (top - 14) * s), fill=col)
    arr[:] = screen(arr, glow_img(lambda d, s: flame(d, s, 1.4, (255, 150, 40)), 30) * 1.2)
    arr[:] = screen(arr, sharp_img(lambda d, s: flame(d, s, 1.0, (255, 214, 120))))
    arr[:] = screen(arr, sharp_img(lambda d, s: flame(d, s, 0.45, (255, 250, 230))))
    return [lambda: label(img, t, t0 + 0.05, "NEXT: THE JELLYFISH UFO", 230, 100, AMBER, "EPISODE 012", WHITE),
            lambda: label(img, t, t0 + 1.2, "REAL STORIES. UNANSWERED QUESTIONS.", 1420, 44, WHITE, None, fnt=FONT_SMB),
            lambda: label(img, t, t0 + 1.8, "FOLLOW FOR THE NEXT STORY.", 1490, 48, AMBER, None, fnt=FONT_SMB)]


# timeline / SC list / IMPACTS for ep011 were:
# ---------------- timeline ----------------
SC = [
    (0.0, ps(3) - 0.25, lambda t, a, i: s_hook(t, a, i)),
    (ps(3) - 0.25, ps(5) - 0.2, lambda t, a, i: s_navy(t, a, i, ps(3) - 0.25)),
    (ps(5) - 0.2, ps(8) - 0.15, lambda t, a, i: s_spectro(t, a, i, ps(5) - 0.2)),
    (ps(8) - 0.15, ps(9) - 0.1, lambda t, a, i: s_pacific(t, a, i, ps(8) - 0.15)),
    (ps(9) - 0.1, ps(11) - 0.3, lambda t, a, i: s_remote(t, a, i, ps(9) - 0.1)),
    (ps(11) - 0.3, ps(14) - 0.2, lambda t, a, i: s_whale(t, a, i, ps(11) - 0.3)),
    (ps(14) - 0.2, ps(17) - 0.2, lambda t, a, i: s_strange(t, a, i, ps(14) - 0.2)),
    (ps(17) - 0.2, ps(20) - 0.4, lambda t, a, i: s_volcano(t, a, i, ps(17) - 0.2)),
    (ps(20) - 0.4, ps(24) - 0.3, lambda t, a, i: s_fade(t, a, i, ps(20) - 0.4, ps(24) - 0.3)),
    (ps(24) - 0.3, TOTAL, lambda t, a, i: s_outro(t, a, i, ps(24) - 0.3)),
]
IMPACTS = [ps(2), ps(8), ps(13), ps(18)]

