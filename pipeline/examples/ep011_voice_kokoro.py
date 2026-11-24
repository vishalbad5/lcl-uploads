# Builds the narration phrase by phrase so every pause, pace change and emphasis is controlled.
import json, numpy as np, soundfile as sf, subprocess, os
from kokoro_onnx import Kokoro
SR=24000
k=Kokoro("models/kokoro.onnx","models/voices.bin")
# text, speed, pause_after(s), pitch(semitones), gain(dB), flags
S=[
 ("The Bloop was solved.",              0.92,0.30, 0.0, 0,"hook"),
 ("But this sound...",                  0.86,0.45, 0.0, 0,""),
 ("never was.",                         0.80,0.85,-0.6, 1,"hit"),
 ("In nineteen ninety-one, a US Navy system built to hunt Soviet submarines",1.06,0.12,0,0,"breath"),
 ("picked up something else.",          0.88,0.60,-0.4, 0,""),
 ("A rising wail.",                     0.84,0.30, 0.0, 0,""),
 ("Again. And again.",0.90,0.22,0.0, 0,""),
 ("Like a siren... under the sea.",     0.84,0.20,-0.3, 0,"sound"),   # sound feature follows
 ("It was so loud, it was heard across the entire Pacific Ocean!",1.04,0.40,0.7,1.5,"breath excite"),
 ("They traced it to one of the emptiest places on Earth.",0.95,0.25,0,0,""),
 ("Thousands of miles from any shore.", 0.90,0.60,-0.3, 0,""),
 ("At first, they blamed whales.",      0.97,0.30, 0.2, 0,"breath"),
 ("But the sound was too steady...",    0.90,0.25, 0.0, 0,""),
 ("to be alive.",                       0.82,0.65,-0.5, 0,"hit"),
 ("And then, it got stranger.",         0.90,0.30, 0.0, 0,""),
 ("Every spring, and every autumn, it grows louder.",0.97,0.35,0.3,0.5,""),
 ("And no one knows why.",              0.84,0.70,-0.5, 0,"sigh"),
 ("The best guess?",                    0.92,0.35, 0.3, 0,""),
 ("A hidden, underwater volcano.",      0.92,0.30, 0.0, 0,""),
 ("But no one has ever found the source.",0.90,0.70,-0.3,0,""),
 ("And since nineteen ninety-one...",                  0.88,0.35, 0.0, 0,"breath"),
 ("it's been getting quieter.",         0.84,0.45,-0.3, 0,""),
 ("As if something down there...",      0.80,0.35,-0.6,-2,"whisper"),
 ("is going silent.",                   0.74,1.10,-0.9,-3,"whisper hit"),
 ("Next: the jellyfish UFO the military filmed. Follow, so you don't miss it.",1.08,0.3,0.3,0,"outro"),
]
SOUND_GAP=2.7   # seconds of the recreated Upsweep after the "siren" line

def trim(a,th=0.012):
    idx=np.where(np.abs(a)>th)[0]
    if len(idx)==0: return a
    s=max(0,idx[0]-int(0.02*SR)); e=min(len(a),idx[-1]+int(0.06*SR))
    return a[s:e]

def proc(a,pitch,gain,whisper):
    sf.write("tmp_in.wav",a,SR)
    f=[]
    if abs(pitch)>0.01: f.append(f"rubberband=pitch={2**(pitch/12):.5f}:formant=preserved")
    if whisper: f.append("highpass=f=180,treble=g=3")
    f.append(f"volume={gain}dB")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i","tmp_in.wav","-af",",".join(f),"-ar",str(SR),"tmp_out.wav"],check=True)
    b,_=sf.read("tmp_out.wav"); return b

rng=np.random.default_rng(7)
def breath(dur=0.42,level=0.022,exhale=False):
    n=int(dur*SR); x=rng.standard_normal(n)
    # pink-ish noise
    X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/SR); X/=np.maximum(f,30)**0.5
    band=((f>350)&(f<3200)).astype(float) if not exhale else ((f>200)&(f<1800)).astype(float)
    x=np.fft.irfft(X*band,n); x/=np.abs(x).max()+1e-9
    t=np.linspace(0,1,n)
    env=(np.sin(np.pi*t**(0.7 if not exhale else 0.35)))**1.6
    if exhale: env*=np.exp(-2.2*t)*1.6
    return x*env*level

out=[]; meta=[]; t=0.25
out.append(np.zeros(int(0.25*SR)))
for i,(txt,sp,pause,pitch,gain,fl) in enumerate(S):
    if "breath" in fl:
        b=breath(); out.append(b); t+=len(b)/SR
    if "sigh" in fl:
        b=breath(0.65,0.03,exhale=True); out.append(b); t+=len(b)/SR; out.append(np.zeros(int(0.08*SR))); t+=0.08
    a,sr=k.create(txt,voice="bm_george",speed=min(1.15,sp+0.07),lang="en-gb")
    a=trim(a); a=proc(a,pitch,gain,"whisper" in fl)
    meta.append(dict(i=i,text=txt,start=round(t,3),end=round(t+len(a)/SR,3),flags=fl))
    out.append(a); t+=len(a)/SR
    p=pause*0.72+(SOUND_GAP if "sound" in fl else 0)
    if "sound" in fl: meta[-1]["sound_at"]=round(t+0.2,3)
    out.append(np.zeros(int(p*SR))); t+=p
v=np.concatenate(out).astype(np.float32)
v=v/np.abs(v).max()*0.89
sf.write("voice_raw.wav",v,SR)
json.dump(dict(total=round(t,3),phrases=meta),open("voice_meta.json","w"),indent=1)
print("total",round(t,2))
for m in meta: print(f'{m["start"]:6.2f}-{m["end"]:6.2f} {m["text"]}')
