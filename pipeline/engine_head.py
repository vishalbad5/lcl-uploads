# Ep 011 "The Upsweep" renderer — 1080x1920, 30 fps, code-drawn cinematic scenes.
import json, math, sys, os, subprocess, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import soundfile as sf

W, H, FPS = 1080, 1920, 30
META = json.load(open("voice_meta.json"))
P = META["phrases"]
TOTAL = META["total"]
SOUND_AT = 9999
rng = np.random.default_rng(11)

FONT_CAP = "/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf"
FONT_BIG = "/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"
FONT_SM = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FONT_SMB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
_fc = {}
def font(path, size, var=None):
    k = (path, size, var)
    if k not in _fc:
        f = ImageFont.truetype(path, size)
        if var: f.set_variation_by_name(var)
        _fc[k] = f
    return _fc[k]

AMBER = (255, 181, 71); CYAN = (90, 230, 255); RED = (255, 64, 64); WHITE = (245, 245, 240)

def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def eout(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ps(i): return P[i]["start"]
def pe(i): return P[i]["end"]

# ---------------- audio-reactive envelopes ----------------
up, usr = np.zeros(48000), 48000
def env_from(x, sr):
    hop = sr // FPS; n = len(x) // hop
    e = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)); return e / (e.max() + 1e-9)
UPENV = env_from(up, usr)
MIXENV = np.zeros(10)
def upenv(t):
    i = int((t - SOUND_AT) * FPS); return float(UPENV[i]) if 0 <= i < len(UPENV) else 0.0
def mixenv(t):
    i = int(t * FPS); return float(MIXENV[i]) if 0 <= i < len(MIXENV) else 0.0

# ---------------- captions ----------------
DISPLAY = {"nineteen ninety-one": "1991"}
HL = set("""military jellyfish sky 2017 infrared blimp iraq something head tentacles engine heat nothing seventeen minutes leaked millions dived water pentagon answer balloons cluster wind closed quite viral alaska military shape kite woman wasnt balloons telling lighthouse vanished follow""".split())
REDW = {"nothing", "balloons", "wasnt", "telling", "quite"}
def syl(w):
    w = w.lower(); n = len(re.findall(r"[aeiouy]+", w)); return max(1, n) + (3 if w.isdigit() else 0)
CAPS = []
WORDS = json.load(open("words.json")) if os.path.exists("words.json") else None
for p in (P if WORDS else []):
    txt = p["text"]
    for a, b in DISPLAY.items(): txt = txt.replace(a, b)
    txt = txt.replace("U.F.O.", "UFO").replace("...", "…")
    words = txt.split()
    # chunk: break after punctuation or 4 words
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 4 or w[-1] in ".,?!…:" and len(cur) >= 2:
            chunks.append(cur); cur = []
    if cur:
        if chunks and len(cur) == 1: chunks[-1] += cur
        else: chunks.append(cur)
    wt_all = WORDS[str(p["i"])]  # list of [start,end] per word
    k = 0
    for c in chunks:
        ws = wt_all[k:k + len(c)]; k += len(c)
        CAPS.append(dict(words=c, start=ws[0][0], end=ws[-1][1], wstarts=[w[0] for w in ws], phrase=p["i"]))
# hold each caption until next starts (max +0.6s)
for i, c in enumerate(CAPS):
    nxt = CAPS[i + 1]["start"] if i + 1 < len(CAPS) else c["end"] + 0.6
    c["hold"] = min(nxt, c["end"] + 0.6)

def draw_caption(img, t):
    cur = None
    for c in CAPS:
        if c["start"] <= t < c["hold"]: cur = c
    if cur is None: return
    f = font(FONT_CAP, 86, "Black")
    words = [w.upper() for w in cur["words"]]
    # layout (wrap to 2 lines if too wide)
    space = 24
    sizes = [f.getbbox(w) for w in words]; widths = [b[2] - b[0] for b in sizes]
    lines, line, lw = [], [], 0
    for w, wd in zip(words, widths):
        if line and lw + space + wd > 940: lines.append(line); line, lw = [], 0
        line.append((w, wd)); lw += (space if lw else 0) + wd
    lines.append(line)
    lh = 108; total_h = lh * len(lines)
    layer = Image.new("RGBA", (W, total_h + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    idx = 0; y = 20
    for ln in lines:
        lwid = sum(wd for _, wd in ln) + space * (len(ln) - 1); x = (W - lwid) // 2
        for w, wd in ln:
            key = re.sub(r"[^a-z0-9]", "", w.lower())
            spoken = t >= cur["wstarts"][idx] - 0.03
            col = (RED if key in REDW else AMBER) if key in HL else WHITE
            if not spoken: col = tuple(int(c * 0.55) for c in WHITE)
            d.text((x, y), w, font=f, fill=col + (255,), stroke_width=7, stroke_fill=(0, 0, 0, 235))
            x += wd + space; idx += 1
        y += lh
    # pop-in
    k = eout((t - cur["start"]) / 0.14); sc = 1.12 - 0.12 * k
    if sc != 1:
        nw, nh = int(layer.width * sc), int(layer.height * sc)
        layer = layer.resize((nw, nh), Image.BICUBIC)
    shadow = layer.split()[3].filter(ImageFilter.GaussianBlur(10))
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0)); sh.putalpha(shadow.point(lambda v: int(v * 0.6)))
    cy = 1235
    img.alpha_composite(sh, ((W - layer.width) // 2, cy - layer.height // 2 + 8))
    img.alpha_composite(layer, ((W - layer.width) // 2, cy - layer.height // 2))

# ---------------- shared layers ----------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.75 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)).clip(0.18, 1)[..., None]
GRAIN = [rng.normal(0, 5.5, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]

def grad(top, bot, power=1.0):
    k = (np.linspace(0, 1, H) ** power)[:, None, None]
    a = np.array(top, np.float32)[None, None] * (1 - k) + np.array(bot, np.float32)[None, None] * k
    return np.broadcast_to(a, (H, W, 3)).copy()

def make_rays():
    small = Image.new("L", (540, 960), 0); d = ImageDraw.Draw(small)
    r = np.random.default_rng(5)
    for _ in range(14):
        x = r.uniform(-100, 640); wdt = r.uniform(12, 55); sk = r.uniform(-140, 140)
        d.polygon([(x, -10), (x + wdt, -10), (x + wdt + sk + wdt * 2, 980), (x + sk - wdt, 980)], fill=int(r.uniform(40, 110)))
    small = small.filter(ImageFilter.GaussianBlur(14))
    a = np.asarray(small, np.float32) / 255 * np.linspace(1, 0, 960)[:, None] ** 1.6
    return np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
RAYS = make_rays()

# marine snow (3D particles)
NP = 260
PX = rng.uniform(-1, 1, NP); PY = rng.uniform(-1, 1, NP); PZ = rng.uniform(0.05, 1, NP); PB = rng.uniform(0.4, 1, NP)
def snow(arr, t, speed=0.05, drift=(0.0, -0.012), bright=1.0, color=(170, 210, 225)):
    lay = Image.new("L", (W, H), 0); d = ImageDraw.Draw(lay)
    z = (PZ - t * speed) % 1.0 + 0.02
    x = ((PX + drift[0] * t + 0.03 * np.sin(t * 0.7 + PY * 6)) % 2 - 1) / z * 0.22 * W + W / 2
    y = ((PY + drift[1] * t) % 2 - 1) / z * 0.22 * H * 0.56 + H / 2
    r = np.clip(2.6 / z, 1, 16)
    a = np.clip((1 - z) * 1.4, 0, 1) * PB * bright * 200
    for xi, yi, ri, ai in zip(x, y, r, a):
        if -20 < xi < W + 20 and -20 < yi < H + 20:
            d.ellipse((xi - ri, yi - ri, xi + ri, yi + ri), fill=int(ai * 0.45))
            d.ellipse((xi - ri * 0.45, yi - ri * 0.45, xi + ri * 0.45, yi + ri * 0.45), fill=int(ai))
    s = np.asarray(lay, np.float32)[..., None] / 255
    arr += s * np.array(color, np.float32)[None, None] * 0.9

def glow_img(draw_fn, blur=18, scale=4):
    sm = Image.new("RGB", (W // scale, H // scale), 0); d = ImageDraw.Draw(sm); draw_fn(d, 1 / scale)
    sm = sm.filter(ImageFilter.GaussianBlur(blur / scale))
    return np.asarray(sm.resize((W, H), Image.BILINEAR), np.float32)

def sharp_img(draw_fn):
    im = Image.new("RGB", (W, H), 0); d = ImageDraw.Draw(im); draw_fn(d, 1.0); return np.asarray(im, np.float32)

def screen(arr, add):  # screen blend
    return 255 - (255 - arr) * (255 - np.clip(add, 0, 255)) / 255

def label(img, t, t0, text, y=330, size=96, col=WHITE, sub=None, subcol=AMBER, t1=None, fnt=FONT_BIG):
    if t < t0 or (t1 is not None and t > t1 + 0.25): return
    k = 1.0 if t0 <= 0.2 else eout((t - t0) / 0.3); out = 1.0 if t1 is None else 1 - ease((t - t1) / 0.25)
    a = int(255 * k * out)
    lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = font(fnt, size); bw = d.textbbox((0, 0), text, font=f)
    x = (W - (bw[2] - bw[0])) // 2
    d.text((x, 20), text, font=f, fill=col + (a,), stroke_width=4, stroke_fill=(0, 0, 0, int(a * 0.8)))
    if sub:
        fs = font(FONT_SM, 40); bs = d.textbbox((0, 0), sub, font=fs)
        d.text(((W - (bs[2] - bs[0])) // 2, 40 + (bw[3] - bw[1]) + 22), sub, font=fs, fill=subcol + (a,), stroke_width=3, stroke_fill=(0, 0, 0, int(a * 0.8)))
    dy = int((1 - k) * 30)
    img.alpha_composite(lay, (0, y + dy))

def tag(img, t, t0, text, xy, col=CYAN, size=34, t1=None):
    if t < t0 or (t1 is not None and t > t1): return
    k = eout((t - t0) / 0.25); n = int(len(text) * min(1, (t - t0) / 0.5))
    d = ImageDraw.Draw(img); f = font(FONT_SM, size)
    d.text(xy, text[:n], font=f, fill=col + (int(255 * k),), stroke_width=3, stroke_fill=(0, 0, 0, 200))

