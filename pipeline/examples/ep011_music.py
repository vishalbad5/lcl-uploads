import json, numpy as np, soundfile as sf, subprocess
SR=48000
M=json.load(open("voice_meta.json")); P=M["phrases"]
T=M["total"]+0.6
N=int(T*SR); t=np.arange(N)/SR
rng=np.random.default_rng(3)
def at(i): return P[i]["start"]
def env_seg(a,b,fi=0.5,fo=0.5):
    e=np.clip((t-a)/max(fi,1e-3),0,1)*np.clip((b-t)/max(fo,1e-3),0,1); return e
def lp(x,fc):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); return np.fft.irfft(X/(1+(f/fc)**4),len(x))
def bp(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); return np.fft.irfft(X*((f>lo)&(f<hi)),len(x))
def saw(freq,ph=0): return 2*((freq*t+ph)%1)-1
L=np.zeros(N); R=np.zeros(N)
def add(x,pan=0,g=1.0,start=0):
    s=int(start*SR); x=x[:N-s]
    L[s:s+len(x)]+=x*g*np.sqrt(0.5*(1-pan)); R[s:s+len(x)]+=x*g*np.sqrt(0.5*(1+pan))

sound_at=[p for p in P if "sound_at" in p][0]["sound_at"]
i_silent=[p["i"] for p in P if "whisper hit" in p["flags"]][0]
outro=P[-1]["start"]
end_music=P[i_silent]["end"]+0.3

# 1) Ocean bed: brown noise, low-passed, slowly breathing
bn=np.cumsum(rng.standard_normal(N)); bn-=lp(bn,0.5); bn=lp(bn,260); bn/=np.abs(bn).max()
breathe=0.6+0.4*np.sin(2*np.pi*t/7.0)
add(bn*breathe*env_seg(0,end_music,0.05,2.5),-0.2,0.20)
bn2=np.cumsum(rng.standard_normal(N)); bn2-=lp(bn2,0.5); bn2=lp(bn2,240); bn2/=np.abs(bn2).max()
add(bn2*breathe*env_seg(0,end_music,0.05,2.5),0.2,0.20)

# 2) Drone: detuned saws in D minor, filter opens with tension
root=73.42
drone=np.zeros(N)
for f,g in [(root,1),(root*1.004,0.9),(root*1.5,0.5),(root*2*1.002,0.35),(root*1.189,0.25)]:
    drone+=g*saw(f,rng.random())
drone=lp(drone,330); drone/=np.abs(drone).max()
tension=np.interp(t,[0,5,20,22.3,30,45,50,55,end_music],[0.55,0.6,0.7,0.95,0.75,0.85,1.0,0.7,0.0])
add(drone*tension*env_seg(0,end_music,1.5,2.0),0,0.17)

# 3) High eerie pad (sine cluster with slow vibrato) for wonder sections
pad=np.zeros(N)
for f in [587.3,880,1174.7,1318.5]:
    pad+=np.sin(2*np.pi*f*t+3*np.sin(2*np.pi*0.21*t+f))
pad/=np.abs(pad).max()
add(pad*env_seg(sound_at+2.6,at(11),3,3),-0.4,0.025)
add(pad*env_seg(at(14),end_music,4,3),0.4,0.03)

# 4) Heartbeat pulse in Navy section and "stranger" section
def thump(dur=0.35,f0=55):
    n=int(dur*SR); tt=np.arange(n)/SR
    return np.sin(2*np.pi*(f0*tt+20*(1-np.exp(-tt*25))/25))*np.exp(-tt*9)
def beats(a,b,bpm):
    p=60/bpm; x=a
    while x<b:
        add(thump(),0,0.32,x); add(thump(0.3,48),0,0.20,x+0.28); x+=p
beats(at(3),at(5)-0.2,64)
beats(at(14),at(16)+1.5,70)

# 5) Sonar pings in Navy scene
def ping(f=1450,dur=1.6):
    n=int(dur*SR); tt=np.arange(n)/SR
    x=np.sin(2*np.pi*f*tt)*np.exp(-tt*3.2)
    # echo tail
    y=x.copy()
    for d,g in [(0.23,0.45),(0.47,0.25),(0.71,0.13)]:
        s=int(d*SR); y[s:]+=x[:n-s]*g
    return y
for k,x0 in enumerate(np.arange(at(3)+0.3,at(5),1.9)):
    add(ping(),(-0.5 if k%2 else 0.5),0.07,x0)

# 6) Impacts
def impact(dur=3.0):
    n=int(dur*SR); tt=np.arange(n)/SR
    boom=np.sin(2*np.pi*(38*tt+30*(1-np.exp(-tt*6))/6))*np.exp(-tt*1.6)
    nz=rng.standard_normal(n); nz=bp(nz,60,900)*np.exp(-tt*4); nz/=np.abs(nz).max()
    return boom*0.9+nz*0.35
for x0,g in [(P[2]["start"]-0.05,0.55),(at(8)-0.05,0.5),(P[13]["start"]-0.05,0.45),(at(18)-0.05,0.5),(P[i_silent]["start"]-0.05,0.35)]:
    add(impact(),0,g,x0)

# 7) Risers (reverse swell) into big moments
def riser(dur):
    n=int(dur*SR); tt=np.arange(n)/SR
    nz=rng.standard_normal(n); nz=bp(nz,300,6000); nz/=np.abs(nz).max()
    sweep=np.sin(2*np.pi*(200*tt+ (900/dur)*tt**2/2))
    e=(tt/dur)**2.5
    return (nz*0.6+sweep*0.25)*e
for x1,d in [(P[2]["start"],1.4),(at(8),2.2),(at(18),1.8)]:
    add(riser(d),0,0.16,x1-d)

# 8) THE UPSWEEP recreation: train of narrow-band rising sweeps with hydrophone hiss + long reverb
def upsweep_train(n_sweeps=4,period=0.66,sweep=0.5):
    dur=n_sweeps*period+2.0; n=int(dur*SR); tt=np.arange(n)/SR; y=np.zeros(n)
    for k in range(n_sweeps):
        s=int(k*period*SR); m=int(sweep*SR); u=np.arange(m)/SR
        f0,f1=330+12*k,690+20*k
        ph=2*np.pi*(f0*u+(f1-f0)*u**2/(2*sweep))
        e=np.sin(np.pi*u/sweep)**0.8
        tone=(np.sin(ph)+0.3*np.sin(2*ph)+0.12*np.sin(3*ph))*e
        y[s:s+m]+=tone*(0.8+0.2*k/n_sweeps)
    # reverb: decaying noise convolution
    ir_n=int(1.6*SR); ir=rng.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR*3.0); ir/=np.sqrt((ir**2).sum())
    wet=np.convolve(y,ir)[:n]*0.9
    hiss=bp(rng.standard_normal(n),800,7000)*0.05
    out=y*0.7+wet+hiss*np.clip(tt/0.3,0,1)*np.clip((dur-tt)/0.5,0,1)
    return out/np.abs(out).max()
up=upsweep_train(); sf.write("upsweep.wav",up,SR)
add(up,0,0.42,sound_at)
# faint echoes of the sweep later (callback motif)
add(upsweep_train(2,0.7,0.5),0.6,0.08,at(16)+0.4)
add(upsweep_train(1,0.7,0.6),-0.6,0.05,at(21)+0.3)

# 9) Outro: warm candle tone (soft bell + low pad)
def bell(f,dur=3.5):
    n=int(dur*SR); tt=np.arange(n)/SR
    return sum(g*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*d) for r,g,d in [(1,1,1.3),(2.76,0.4,2.5),(5.4,0.2,4),(0.5,0.3,1.0)])
add(bell(293.66),-0.2,0.10,outro-0.2)
add(bell(440),0.2,0.06,outro+1.6)
add(lp(saw(146.83)+saw(220.5),500)*env_seg(outro-0.3,T,1.2,0.8),0,0.04)

mus=np.stack([L,R],1); mus/=np.abs(mus).max(); mus*=0.9
sf.write("music.wav",mus.astype(np.float32),SR)
print("music",T, "sound_at",sound_at)
