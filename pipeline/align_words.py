# Word timings for captions. Input: voice_raw.wav (mono) + voice_meta.json {"total", "phrases":[{i,text,start,end}]}
# Output: words.json {"<i>": [[start,end], ...]} (one entry per word of the phrase text, "..." removed)
import json, re, sys, numpy as np, soundfile as sf
M = json.load(open("voice_meta.json")); P = M["phrases"]
v, sr = sf.read("voice_raw.wav")
if v.ndim > 1: v = v.mean(1)
def syl(w):
    w = re.sub(r"[^a-z0-9]", "", w.lower())
    return 4 if w.isdigit() else max(1, len(re.findall(r"[aeiouy]+", w)))
words = {}
for p in P:
    seg = v[int(p["start"] * sr):int(p["end"] * sr)]
    hop = sr // 100; n = len(seg) // hop
    e = np.sqrt((seg[:n * hop].reshape(n, hop) ** 2).mean(1)); th = max(0.012, e.max() * 0.06)
    vo = e > th; idx = np.where(vo)[0]
    if len(idx) == 0: idx = np.arange(n)
    vo2 = np.zeros(n, bool); vo2[idx] = True
    for a, b in zip(idx[:-1], idx[1:]):
        if b - a <= 6: vo2[a:b] = True
    vt = np.where(vo2)[0]
    W = [w for w in p["text"].replace("...", " ").split() if re.sub(r"[^A-Za-z0-9]", "", w)]
    sy = np.array([syl(w) for w in W], float); cum = np.concatenate([[0], np.cumsum(sy)]) / sy.sum()
    words[str(p["i"])] = [[round(p["start"] + vt[min(len(vt) - 1, int(cum[k] * len(vt)))] / 100, 3),
                           round(p["start"] + (vt[min(len(vt) - 1, int(cum[k + 1] * len(vt)) - 1)] + 1) / 100, 3)] for k in range(len(W))]
json.dump(words, open("words.json", "w")); print("words.json written for", len(words), "phrases")
