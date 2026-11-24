# ---------------- Ep 012 scenes: thermal-camera look ----------------
SUB = json.load(open("subs.json"))
GRN = (150, 255, 170)
TH_NOISE = [rng.normal(0, 7, (H // 3, W // 3)).astype(np.float32) for _ in range(5)]
def thermal_bg(arr, t, base=70, var=26):
    # grayscale IR background: soft cloud texture + sensor noise
    cl = (np.sin(xx / 210 + t * 0.15) * np.sin(yy / 260 - t * 0.1) + np.sin((xx + yy) / 330 + t * 0.07)) * var
    g = base + cl + np.repeat(np.repeat(TH_NOISE[int(t * 30) % 5], 3, 0), 3, 1)[:H, :W]
    arr[:] = np.stack([g, g, g], 2)

def jelly(d, s, x, y, sz, t, col=(255, 255, 255), tent_col=None):
    tent_col = tent_col or col
    # dome head
    d.pieslice(((x - sz) * s, (y - sz * 0.8) * s, (x + sz) * s, (y + sz * 0.8) * s), 180, 360, fill=col)
    d.ellipse(((x - sz) * s, (y - sz * 0.18) * s, (x + sz) * s, (y + sz * 0.18) * s), fill=col)
    for k in range(5):
        x0 = x - sz * 0.7 + k * sz * 0.35
        pts = []
        for j in range(14):
            u = j / 13
            pts.append(((x0 + math.sin(t * 2.2 + k * 1.3 + u * 4) * sz * 0.18 * u) * s, (y + 8 + u * sz * (1.7 + 0.25 * math.sin(k))) * s))
        d.line(pts, fill=tent_col, width=max(1, int(sz * 0.12 * s)))

def hud(img, t, obj=None, label="IR  WHT  NFOV", zoomtxt="x8.0", clock0=0, show_trk=True):
    d = ImageDraw.Draw(img); f = font(FONT_SM, 30); c = (235, 235, 235, 230)
    # crosshair
    cx, cy = W // 2, 900
    for (a, b) in [((cx - 120, cy), (cx - 40, cy)), ((cx + 40, cy), (cx + 120, cy)), ((cx, cy - 120), (cx, cy - 40)), ((cx, cy + 40), (cx, cy + 120))]:
        d.line([a, b], fill=c, width=4)
    # corner brackets
    for (x, y, sx, sy) in [(90, 560, 1, 1), (990, 560, -1, 1), (90, 1240, 1, -1), (990, 1240, -1, -1)]:
        d.line([(x, y), (x + 70 * sx, y)], fill=c, width=5); d.line([(x, y), (x, y + 70 * sy)], fill=c, width=5)
    d.text((70, 170), label, font=f, fill=c); d.text((70, 210), f"AZ {214.6 + 0.8 * math.sin(t * 0.3):05.1f}  EL -{12.3 + 0.2 * math.sin(t * 0.5):04.1f}", font=f, fill=c)
    secs = clock0 + t
    d.text((760, 170), f"{int(secs // 3600):02d}:{int(secs // 60) % 60:02d}:{int(secs) % 60:02d}", font=f, fill=c)
    d.text((760, 210), zoomtxt, font=f, fill=c)
    # scale ticks
    for k in range(9): d.line([(1010, 620 + k * 70), (1035 if k % 2 else 1050, 620 + k * 70)], fill=c, width=3)
    if obj and show_trk:
        ox, oy, r = obj
        d.rectangle((ox - r, oy - r, ox + r, oy + r), outline=(255, 255, 255, 220), width=3)
        d.text((ox - r, oy - r - 38), "TRK", font=f, fill=(255, 255, 255, 230))

def ir_object(arr, t, x, y, sz, hot=210):
    m = sharp_img(lambda d, s: jelly(d, s, x, y, sz, t, (255, 255, 255)))
    g = glow_img(lambda d, s: jelly(d, s, x, y, sz, t, (255, 255, 255)), 14, 2)
    arr[:] = arr * (1 - m / 255) + (m / 255) * hot
    arr[:] = screen(arr, g * 0.35)

def s_hook(t, arr, img):
    thermal_bg(arr, t)
    x = 540 + 40 * math.sin(t * 0.5); y = 900 + 18 * math.sin(t * 0.8); sz = 120 + 10 * ease(t / 4)
    ir_object(arr, t, x, y, sz)
    out = [lambda: hud(img, t, (x, y + 60, 200), clock0=37000),
           lambda: label(img, t, 0.0, "THE JELLYFISH UFO", 300, 120, WHITE, "U.S. MILITARY INFRARED FOOTAGE  ·  RECREATION", AMBER)]
    return out

def blimp(d, s, x, y, L, col):
    d.ellipse(((x - L / 2) * s, (y - L * 0.17) * s, (x + L / 2) * s, (y + L * 0.17) * s), fill=col)
    d.polygon([((x - L * 0.42) * s, y * s), ((x - L * 0.58) * s, (y - L * 0.16) * s), ((x - L * 0.5) * s, y * s), ((x - L * 0.58) * s, (y + L * 0.16) * s)], fill=col)
    d.rectangle(((x - L * 0.06) * s, (y + L * 0.15) * s, (x + L * 0.06) * s, (y + L * 0.22) * s), fill=col)

def s_base(t, arr, img, t0):
    lt = t - t0
    arr[:] = grad((8, 14, 30), (2, 3, 8), 1.0)
    # stars
    def stars(d, s):
        r = np.random.default_rng(3)
        for _ in range(160):
            x, y = r.uniform(0, W), r.uniform(0, 900); b = int(r.uniform(80, 220) * (0.7 + 0.3 * math.sin(t * 3 + x)))
            d.point((x, y), fill=(b, b, b))
    arr[:] = np.maximum(arr, sharp_img(stars))
    # base lights below (perspective grid of lights)
    def lights(d, s):
        for row in range(14):
            yb = 1350 + row ** 1.5 * 14; sp = 30 + row * 9
            for k in range(-12, 13):
                x = 540 + k * sp + (row % 2) * sp / 2
                rr = 2 + row * 0.35
                d.ellipse(((x - rr) * s, (yb - rr) * s, (x + rr) * s, (yb + rr) * s), fill=(255, 190, 110) if (k + row) % 5 else (180, 220, 255))
    arr[:] = screen(arr, glow_img(lights, 10, 2) * 0.9); arr[:] = screen(arr, sharp_img(lights))
    # tethered blimp drifting
    bx = 430 + lt * 14; by = 760 + 10 * math.sin(lt * 0.7)
    tether = sharp_img(lambda d, s: d.line([(bx, by + 120), (560, 1920)], fill=(60, 70, 80), width=3)); arr[:] = np.maximum(arr, tether)
    b = sharp_img(lambda d, s: blimp(d, s, bx, by, 520, (255, 255, 255)))
    arr[:] = arr * (1 - b / 255) + b / 255 * np.array([28, 34, 44], np.float32)
    arr[:] = screen(arr, glow_img(lambda d, s: d.ellipse(((bx - 8) * s, (by + 80) * s, (bx + 8) * s, (by + 96) * s), fill=(255, 60, 60)), 26) * (0.6 + 0.6 * (math.sin(lt * 5) > 0)))
    # camera cone after "An infrared camera"
    if t > SUB["camera"]:
        k = eout((t - SUB["camera"]) / 0.5)
        cone = glow_img(lambda d, s: d.polygon([(bx * s, (by + 90) * s), ((bx - 260) * s, 1500 * s), ((bx + 120) * s, 1500 * s)], fill=(90, 230, 255)), 40)
        arr[:] = screen(arr, cone * 0.35 * k)
    out = [lambda: label(img, t, t0 + 0.05, "OCT 23, 2017", 250, 130, AMBER, "AL TAQADDUM AIR BASE, IRAQ", WHITE),
           lambda: tag(img, t, SUB["camera"], "IR SENSOR ON AEROSTAT  ·  2,700 FT", (150, 560), CYAN, 36)]
    if t > SUB["locks"]:
        out.append(lambda: tag(img, t, SUB["locks"], "▲ TARGET ACQUIRED", (330, 620), RED, 44))
    return out

def s_zoom(t, arr, img, t0):
    lt = t - t0
    thermal_bg(arr, t, 64, 22)
    sz = 210 + 30 * ease(lt / 6); x = 540 + 20 * math.sin(t * 0.6); y = 820
    ir_object(arr, t, x, y, sz)
    out = [lambda: hud(img, t, None, zoomtxt="x24.0", clock0=37000)]
    def callout(txt, t1, p0, p1, col):
        def f():
            if t < t1: return
            k = eout((t - t1) / 0.3); d = ImageDraw.Draw(img)
            ex = p0[0] + (p1[0] - p0[0]) * k; ey = p0[1] + (p1[1] - p0[1]) * k
            d.line([p0, (ex, ey)], fill=col + (255,), width=5); d.ellipse((p0[0] - 10, p0[1] - 10, p0[0] + 10, p0[1] + 10), fill=col + (255,))
            if k > 0.9: d.text((p1[0] - 10, p1[1] - 60), txt, font=font(FONT_BIG, 64), fill=col + (255,), stroke_width=4, stroke_fill=(0, 0, 0, 220))
        return f
    out.append(callout("HEAD", ps(2), (x - 60, y - 120), (150, 560), AMBER))
    out.append(callout("TENTACLES", SUB["dangling"], (x + 80, y + 260), (720, 1360), AMBER))
    if t >= ps(3):
        out.append(lambda: tag(img, t, ps(3), "ENGINE:   NONE", (120, 1430), RED, 52))
        out.append(lambda: tag(img, t, SUB["heat"], "HEAT:       NONE", (120, 1500), RED, 52))
        out.append(lambda: label(img, t, SUB["nothing"], "NOTHING.", 260, 150, RED, None))
    return out

def s_drift(t, arr, img, t0):
    lt = t - t0; dur = ps(5) - t0
    thermal_bg(arr, t, 58, 18)
    # base rooftops (top-down, warm = bright)
    def roofs(d, s):
        r = np.random.default_rng(9)
        for _ in range(26):
            x, y = r.uniform(40, 1000), r.uniform(1100, 1800); w, h = r.uniform(60, 180), r.uniform(40, 120)
            d.rectangle((x, y, x + w, y + h), fill=(150, 150, 150))
    arr[:] = np.maximum(arr, sharp_img(roofs) * 0.9)
    x = 140 + 800 * ease(lt / dur); y = 760 + 40 * math.sin(lt)
    ir_object(arr, t, x, y, 90)
    mins = 17 * ease(lt / dur)
    out = [lambda: hud(img, t, (x, y + 50, 150), zoomtxt="x4.0", clock0=37000),
           lambda: label(img, t, t0 + 0.05, f"{int(mins):02d}:{int(mins * 60) % 60:02d}", 300, 170, WHITE, "MINUTES ON CAMERA", AMBER)]
    return out

def s_leak(t, arr, img, t0):
    lt = t - t0
    if t < SUB["one"] - 0.1:
        arr[:] = grad((14, 10, 24), (2, 2, 6), 1.0)
        # wall of phone screens showing the IR clip
        for k in range(6):
            cx = 200 + (k % 3) * 340; cy = 650 + (k // 3) * 620 + 40 * math.sin(lt + k)
            ph = sharp_img(lambda d, s: d.rounded_rectangle((cx - 140, cy - 260, cx + 140, cy + 260), radius=30, fill=(80, 80, 80)))
            arr[:] = np.maximum(arr, ph)
            ir = sharp_img(lambda d, s: jelly(d, s, cx, cy - 40, 60, t + k, (230, 230, 230)))
            arr[:] = np.maximum(arr, ir)
        views = int(1_000_000 * eout(lt / 2.0))
        return [lambda: label(img, t, t0 + 0.05, f"{views:,} VIEWS", 250, 120, WHITE, "THE FOOTAGE LEAKS  ·  JAN 2024", AMBER)]
    # water + dive claim
    k = (t - SUB["one"]) / max(0.1, ps(6) - SUB["one"])
    thermal_bg(arr, t, 52, 14)
    wl = 1150
    water = sharp_img(lambda d, s: d.rectangle((0, wl, W, H), fill=(255, 255, 255)))
    arr[:] = arr * (1 - water / 255) + water / 255 * (35 + 6 * np.sin(xx / 40 + t * 3)[..., None])
    oy = 700 + 520 * ease((t - SUB["dived"] + 0.3) / 1.2) if t > SUB["dived"] - 0.3 else 700
    if oy < wl + 40: ir_object(arr, t, 540, oy, 90)
    if t > SUB["dived"] + 0.5:
        rr = (t - SUB["dived"] - 0.5) * 300
        arr[:] = screen(arr, sharp_img(lambda d, s: [d.ellipse((540 - rr - j * 60, wl - (rr + j * 60) * 0.12, 540 + rr + j * 60, wl + (rr + j * 60) * 0.12), outline=(160, 160, 160), width=4) for j in range(3)]))
    return [lambda: hud(img, t, None, zoomtxt="x6.0", clock0=38020),
            lambda: label(img, t, SUB["one"], "“IT DIVED INTO THE WATER”", 260, 92, WHITE, "ONE RESEARCHER'S CLAIM  ·  UNVERIFIED", AMBER)]

def balloons(d, s, x, y, sz, t, col):
    r = np.random.default_rng(4)
    for k in range(9):
        bx = x + r.uniform(-1, 1) * sz * 0.9; by = y + r.uniform(-0.6, 0.4) * sz; rr = sz * r.uniform(0.22, 0.38)
        d.ellipse(((bx - rr) * s, (by - rr * 1.15) * s, (bx + rr) * s, (by + rr * 1.15) * s), fill=col)
        d.line([(bx * s, (by + rr * 1.15) * s), ((x + math.sin(t * 2 + k) * 20) * s, (y + sz * 1.8) * s)], fill=col, width=max(1, int(4 * s)))

def s_answer(t, arr, img, t0):
    lt = t - t0
    arr[:] = grad((22, 20, 16), (6, 6, 5), 1.0)
    # document page
    def doc(d, s):
        d.rectangle((120, 480, 960, 1560), fill=(232, 226, 210))
        for k in range(16):
            y = 700 + k * 48; d.line([(190, y), (190 + (600 if k % 4 else 420), y)], fill=(150, 145, 135), width=10)
    arr[:] = np.where(sharp_img(doc).sum(2, keepdims=True) > 0, sharp_img(doc), arr)
    out = [lambda: tag(img, t, t0, "ALL-DOMAIN ANOMALY RESOLUTION OFFICE", (170, 540), (40, 40, 40), 32),
           lambda: tag(img, t, t0 + 0.3, "CASE RESOLUTION  ·  8 SEPT 2025", (170, 590), (120, 30, 30), 34),
           lambda: label(img, t, t0 + 0.05, "THE PENTAGON'S ANSWER", 250, 110, WHITE, None)]
    # morph jellyfish -> balloons (overlay drawn on doc)
    m = ease((t - ps(7) + 0.2) / 0.8)
    def drawobj(d, s):
        if m < 1: jelly(d, s, 540, 1050, 150, t, (int(60 + 0 * m), 60, 60))
    if m < 1:
        o = sharp_img(lambda d, s: jelly(d, s, 540, 1050, 150, t, (255, 255, 255)))
        arr[:] = arr * (1 - o / 255 * (1 - m) * 0.85)
    if m > 0:
        bl = sharp_img(lambda d, s: balloons(d, s, 540, 1000, 170, t, (255, 255, 255)))
        arr[:] = arr * (1 - bl / 255) + bl / 255 * np.array([200, 60, 60], np.float32) * m + arr * (bl / 255) * (1 - m)
    if t > ps(7):
        def stamp():
            k = eout((t - ps(7)) / 0.18); sc = 1.6 - 0.6 * k
            lay = Image.new("RGBA", (900, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            d.rounded_rectangle((10, 10, 890, 250), radius=20, outline=(200, 30, 30, 255), width=14)
            f = font(FONT_BIG, 170); bb = d.textbbox((0, 0), "BALLOONS", font=f)
            d.text(((900 - (bb[2] - bb[0])) // 2, 10), "BALLOONS", font=f, fill=(200, 30, 30, 255))
            lay = lay.rotate(-8, expand=True, resample=Image.BICUBIC)
            lay = lay.resize((int(lay.width * sc), int(lay.height * sc)), Image.BICUBIC)
            lay.putalpha(lay.split()[3].point(lambda v: int(v * min(1, k * 1.5))))
            img.alpha_composite(lay, ((W - lay.width) // 2, 1380 - lay.height // 2))
        out.append(stamp)
        out.append(lambda: tag(img, t, SUB["cluster"], "DRIFTING WITH THE WIND  ·  4-14 MPH", (190, 1500), (40, 40, 40), 34))
    return out

def s_notquite(t, arr, img, t0):
    lt = t - t0
    arr[:] = grad((22, 20, 16), (6, 6, 5), 1.0)
    out = [lambda: label(img, t, t0 + 0.02, "CASE CLOSED?", 600, 150, WHITE, None, t1=SUB["notquite"] - 0.05)]
    if t > SUB["notquite"]:
        gl = (t - SUB["notquite"]) < 0.3
        if gl:
            arr += rng.normal(0, 40, (H, W, 1)).astype(np.float32)
            arr[:, :, 0] = np.roll(arr[:, :, 0], 18, 1)
        out.append(lambda: label(img, t, SUB["notquite"], "NOT QUITE.", 600, 170, RED, None))
    return out

def mountains(d, s, base, col, seed, amp):
    r = np.random.default_rng(seed); n = 60; ys = np.cumsum(r.normal(0, 1, n)); ys = (ys - ys.min()) / (np.ptp(ys) + 1e-9)
    pts = [(i * W / (n - 1), base - ys[i] * amp) for i in range(n)] + [(W, H), (0, H)]
    d.polygon(pts, fill=col)

def s_alaska(t, arr, img, t0):
    lt = t - t0
    arr[:] = grad((70, 96, 140), (230, 170, 120), 1.2)   # dusk sky
    for base, col, seed, amp in [(1250, (60, 66, 84), 1, 320), (1420, (36, 40, 52), 2, 220), (1600, (16, 18, 24), 3, 120)]:
        m = sharp_img(lambda d, s: mountains(d, s, base, (255, 255, 255), seed, amp))
        arr[:] = arr * (1 - m / 255) + m / 255 * np.array(col, np.float32)
    # dark object with streamers, swaying in wind
    ox = 560 + 40 * math.sin(lt * 0.9); oy = 720 + 20 * math.sin(lt * 1.3)
    o = sharp_img(lambda d, s: jelly(d, s, ox, oy, 70, t * 1.6, (255, 255, 255)))
    arr[:] = arr * (1 - o / 255 * 0.88)
    split = t >= ps(10)
    if split:
        # split screen: Iraq IR on the left half
        th = np.zeros_like(arr); thermal_bg(th, t, 64, 20)
        ir_object(th, t, 270, 820, 80)
        arr[:, :W // 2] = th[:, :W // 2]
        arr[:, W // 2 - 3:W // 2 + 3] = 255
    def phone_ui():
        d = ImageDraw.Draw(img); f = font(FONT_SM, 34)
        if not split:
            d.ellipse((70, 180, 100, 210), fill=(255, 40, 40, 255) if int(t * 2) % 2 else (120, 20, 20, 255))
            d.text((115, 172), "REC  00:" + f"{int(lt) % 60:02d}", font=f, fill=(255, 255, 255, 255))
    out = [phone_ui]
    if not split:
        out.append(lambda: label(img, t, t0 + 0.05, "THIS MONTH: VIRAL", 260, 110, AMBER, "FILMED JUNE 2026  ·  WENT VIRAL NOV 2026", WHITE))
        out.append(lambda: tag(img, t, SUB["alaska"], "ANCHORAGE, ALASKA", (300, 1700), WHITE, 46))
        out.append(lambda: tag(img, t, SUB["near"], "NEAR JOINT BASE ELMENDORF-RICHARDSON", (90, 1770), AMBER, 34))
    else:
        out.append(lambda: tag(img, t, ps(10), "IRAQ 2017", (130, 300), WHITE, 50))
        out.append(lambda: tag(img, t, ps(10), "ALASKA 2026", (650, 300), WHITE, 50))
        out.append(lambda: label(img, t, ps(10) + 0.2, "SAME SHAPE", 1500, 120, AMBER, None))
    return out

def s_verdict(t, arr, img, t0):
    arr[:] = grad((10, 12, 20), (2, 2, 6), 1.0)
    def card(y, t1, title, body, col):
        def f():
            if t < t1: return
            k = eout((t - t1) / 0.35); x = int(-900 * (1 - k)) + 90
            d = ImageDraw.Draw(img)
            d.rounded_rectangle((x, y, x + 900, y + 300), radius=26, fill=(20, 22, 30, 235), outline=col + (255,), width=6)
            d.text((x + 40, y + 30), title, font=font(FONT_BIG, 64), fill=col + (255,))
            d.text((x + 40, y + 130), body, font=font(FONT_CAP, 64, "Black"), fill=(245, 245, 240, 255))
        return f
    return [card(430, t0 + 0.05, "EXPERTS", "“PROBABLY A KITE”", CYAN),
            card(800, SUB["but"], "THE WOMAN WHO FILMED IT", "“IT WASN'T A KITE”", RED)]

def s_question(t, arr, img, t0):
    lt = t - t0; dark = ease(lt / (ps(13) - t0))
    arr[:] = grad((8, 8, 14), (0, 0, 2), 1.0) * (1 - 0.5 * dark)
    bl = sharp_img(lambda d, s: balloons(d, s, 300, 820, 120, t, (255, 255, 255)))
    arr[:] = np.maximum(arr, bl * 0.55 * (1 - dark * 0.6))
    o = glow_img(lambda d, s: jelly(d, s, 780, 820, 110, t, (90, 230, 255)), 30)
    arr[:] = screen(arr, o * (0.4 + 0.8 * ease((t - SUB["orsomething"]) / 0.6)))
    arr[:] = screen(arr, sharp_img(lambda d, s: jelly(d, s, 780, 820, 110, t, (200, 245, 255))) * (0.3 + 0.7 * ease((t - SUB["orsomething"]) / 0.6)))
    return [lambda: label(img, t, t0 + 0.05, "BALLOONS…", 300, 130, WHITE, None),
            lambda: label(img, t, SUB["orsomething"], "OR SOMETHING ELSE?", 450, 120, RED, None)]

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
    return [lambda: label(img, t, t0 + 0.05, "NEXT: 3 KEEPERS VANISHED", 230, 96, AMBER, "EPISODE 013", WHITE),
            lambda: label(img, t, t0 + 1.2, "REAL STORIES. UNANSWERED QUESTIONS.", 1420, 44, WHITE, None, fnt=FONT_SMB),
            lambda: label(img, t, t0 + 1.8, "FOLLOW FOR THE NEXT STORY.", 1490, 48, AMBER, None, fnt=FONT_SMB)]

SC = [
    (0.0, ps(1) - 0.15, lambda t, a, i: s_hook(t, a, i)),
    (ps(1) - 0.15, ps(2) - 0.1, lambda t, a, i: s_base(t, a, i, ps(1) - 0.15)),
    (ps(2) - 0.1, ps(4) - 0.2, lambda t, a, i: s_zoom(t, a, i, ps(2) - 0.1)),
    (ps(4) - 0.2, ps(5) - 0.1, lambda t, a, i: s_drift(t, a, i, ps(4) - 0.2)),
    (ps(5) - 0.1, ps(6) - 0.2, lambda t, a, i: s_leak(t, a, i, ps(5) - 0.1)),
    (ps(6) - 0.2, ps(8) - 0.15, lambda t, a, i: s_answer(t, a, i, ps(6) - 0.2)),
    (ps(8) - 0.15, ps(9) - 0.2, lambda t, a, i: s_notquite(t, a, i, ps(8) - 0.15)),
    (ps(9) - 0.2, ps(11) - 0.2, lambda t, a, i: s_alaska(t, a, i, ps(9) - 0.2)),
    (ps(11) - 0.2, ps(12) - 0.2, lambda t, a, i: s_verdict(t, a, i, ps(11) - 0.2)),
    (ps(12) - 0.2, ps(13) - 0.3, lambda t, a, i: s_question(t, a, i, ps(12) - 0.2)),
    (ps(13) - 0.3, TOTAL, lambda t, a, i: s_outro(t, a, i, ps(13) - 0.3)),
]
IMPACTS = [SUB["sky"], SUB["nothing"], ps(7), SUB["notquite"], SUB["orsomething"]]

