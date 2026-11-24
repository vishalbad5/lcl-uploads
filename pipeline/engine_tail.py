def frame(fi, scene_idx):
    t = fi / FPS
    a, b, fn = SC[scene_idx]
    arr = np.zeros((H, W, 3), np.float32)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    overlays = fn(t, arr, img)
    lt = t - a
    # camera: slow push-in + micro drift + impact shake
    z = 1.005 + 0.06 * ease(lt / max(1, b - a)) + 0.004 * math.sin(t * 1.3)
    sh = 0
    for ti in IMPACTS:
        if 0 <= t - ti < 0.35: sh = 14 * (1 - (t - ti) / 0.35)
    arr *= VIG
    arr += np.repeat(np.repeat(GRAIN[fi % 6], 2, 0), 2, 1)[..., None]
    # scene in/out dips
    k = min(1, (t - a) / 0.12 if scene_idx > 0 else 1, (b - t) / 0.08 if scene_idx < len(SC) - 1 else 1)
    arr *= max(0.0, k) ** 0.7
    # impact flash
    for ti in IMPACTS:
        if 0 <= t - ti < 0.18: arr += 60 * (1 - (t - ti) / 0.18)
    base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    if z != 1 or sh:
        cw, ch = W / z, H / z
        ox = (W - cw) / 2 + sh * math.sin(t * 90); oy = (H - ch) / 2 + sh * math.cos(t * 77)
        if sh: cw, ch = W / max(z, 1.03), H / max(z, 1.03); ox = (W - cw) / 2 + sh * math.sin(t * 90); oy = (H - ch) / 2 + sh * math.cos(t * 77)
        ox = min(max(ox, 0), W - cw); oy = min(max(oy, 0), H - ch)
        base = base.resize((W, H), Image.BILINEAR, box=(ox, oy, ox + cw, oy + ch))
    for o in overlays: o()
    base.alpha_composite(img)
    draw_caption(base, t)
    return base.convert("RGB")

def render_scene(si, out):
    a, b, _ = SC[si]
    f0, f1 = int(round(a * FPS)), int(round(b * FPS))
    tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        p.stdin.write(frame(fi, si).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(tmp, out)
    return f1 - f0

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for tt in map(float, sys.argv[2:]):
            si = max(i for i, (a, b, _) in enumerate(SC) if a <= tt)
            frame(int(tt * FPS), si).save(f"still_{tt:05.2f}.jpg", quality=90)
    else:
        for si in map(int, sys.argv[2:]):
            n = render_scene(si, f"scene_{si:02d}.mp4"); print("scene", si, n, flush=True)
