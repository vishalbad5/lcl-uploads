import json, numpy as np, soundfile as sf
SR=48000
M=json.load(open("voice_meta.json")); P=M["phrases"]; SUB=json.load(open("subs.json")) if __import__("os").path.exists("subs.json") else {}
T=M["total"]; N=int(T*SR); t=np.arange(N)/SR
rng=np.random.default_rng(5)
def ps(i): return P[i]["start"]
def pe(i): return P[i]["end"]
def sub(k,default): return SUB.get(k,default)
def env_seg(a,b,fi=0.5,fo=0.5): return np.clip((t-a)/max(fi,1e-3),0,1)*np.clip((b-t)/max(fo,1e-3),0,1)
def lp(x,fc):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); return np.fft.irfft(X/(1+(f/fc)**4),len(x))
def bp(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); return np.fft.irfft(X*((f>lo)&(f<hi)),len(x))
def saw(freq,ph=0): return 2*((freq*t+ph)%1)-1
L=np.zeros(N); R=np.zeros(N)
def add(x,pan=0,g=1.0,start=0):
    s=int(start*SR)
    if s>=N: return
    x=x[:N-s]; L[s:s+len(x)]+=x*g*np.sqrt(0.5*(1-pan)); R[s:s+len(x)]+=x*g*np.sqrt(0.5*(1+pan))
SKY=sub("sky",ps(0)+2.7); NOTHING=sub("nothing",ps(3)+2.3); NOTQ=sub("notquite",ps(8)+1.4); ALASKA=sub("alaska",ps(9)+2.6); OR=sub("orsomething",ps(12)+1.8)
outro=ps(13); endm=pe(12)+0.5
# thermal-camera static/hum bed for the Iraq section
st=bp(rng.standard_normal(N),1500,7000); st/=np.abs(st).max()
add(st*env_seg(0,ps(6),0.05,1.0)*(0.6+0.4*np.sin(2*np.pi*t*0.37)),0,0.016)
hum=np.sin(2*np.pi*60*t)+0.4*np.sin(2*np.pi*120*t); add(hum*env_seg(0,ps(6),0.05,1),0,0.012)
# drone (E minor) with tension curve
root=82.41; dr=np.zeros(N)
for f,g in [(root,1),(root*1.005,.9),(root*1.5,.45),(root*2.003,.3),(root*1.189,.22)]: dr+=g*saw(f,rng.random())
dr=lp(dr,300); dr/=np.abs(dr).max()
ten=np.interp(t,[0,4,12,19.3,23,30,33.8,38,41.4,51,57,endm],[.6,.7,.8,.95,.7,.85,1,.6,.8,.85,.95,0])
add(dr*ten*env_seg(0,endm,0.05,1.5),0,0.17)
# pulsing synth bass
def pulse_section(a,b,bpm=100,f=41.2,g=0.13):
    p=60/bpm/2; x=a; k=0
    while x<b:
        n=int(0.22*SR); tt=np.arange(n)/SR
        y=np.tanh(2.5*np.sin(2*np.pi*(f*(2 if k%4==3 else 1))*tt))*np.exp(-tt*9)
        add(y,0,g,x); x+=p; k+=1
pulse_section(ps(1),NOTHING-0.1)
pulse_section(ps(4),ps(6)-0.2,104,41.2,0.11)
pulse_section(ALASKA,ps(12)-0.2,92,38.9)
# HUD beeps
def beep(f=2100,d=0.07):
    n=int(d*SR); tt=np.arange(n)/SR; return np.sin(2*np.pi*f*tt)*np.sin(np.pi*tt/d)
for x0 in [ps(0)+0.05,ps(1),ps(2),ps(2)+1.5,ps(3),ps(3)+0.9,ps(3)+1.7]:
    add(beep(),0.3,0.08,x0); add(beep(2800,0.05),0.3,0.06,x0+0.1)
for x0 in np.arange(ps(4),pe(4),0.5): add(beep(1600,0.04),-0.3,0.04,x0)
# impacts
def impact(dur=3.0):
    n=int(dur*SR); tt=np.arange(n)/SR
    boom=np.sin(2*np.pi*(36*tt+30*(1-np.exp(-tt*6))/6))*np.exp(-tt*1.6)
    nz=bp(rng.standard_normal(n),60,900)*np.exp(-tt*4); nz/=np.abs(nz).max()
    return boom*0.9+nz*0.35
for x0,g in [(SKY,.55),(NOTHING,.45),(ps(7),.6),(NOTQ,.45),(ALASKA,.35),(OR,.35)]: add(impact(),0,g,x0-0.04)
def riser(d):
    n=int(d*SR); tt=np.arange(n)/SR; nz=bp(rng.standard_normal(n),300,6000); nz/=np.abs(nz).max()
    sw=np.sin(2*np.pi*(200*tt+(900/d)*tt**2/2)); return (nz*.6+sw*.25)*(tt/d)**2.5
for x1,d in [(SKY,1.3),(ps(7),2.4),(ALASKA,1.5)]: add(riser(d),0,0.16,x1-d)
# water splash-ish for "dived into the water"
n=int(1.5*SR); tt=np.arange(n)/SR; sp=bp(rng.standard_normal(n),300,4000)*np.exp(-tt*3)*(1-np.exp(-tt*60))
add(sp/np.abs(sp).max(),0,0.06,sub("dived",ps(5)+5.0))
# glitch at "Not quite"
n=int(0.35*SR); g=rng.standard_normal(n)*(np.sign(np.sin(np.arange(n)/SR*2*np.pi*23))*0.5+0.5)*np.exp(-np.arange(n)/SR*6)
add(bp(g,200,8000),0,0.12,NOTQ-0.05)
# stamp thud for "Balloons"
add(impact(1.2),0,0.25,ps(7)+0.02)
# eerie pad for Alaska + ending
pad=np.zeros(N)
for f in [659.3,987.8,1318.5,1480]: pad+=np.sin(2*np.pi*f*t+3*np.sin(2*np.pi*0.19*t+f))
pad/=np.abs(pad).max(); add(pad*env_seg(ps(9),endm,3,2.5),0,0.028)
wd=bp(rng.standard_normal(N),200,1200); wd/=np.abs(wd).max()
add(wd*env_seg(ps(9),ps(12),1,1)*(0.5+0.5*np.sin(2*np.pi*t*0.23)),0,0.03)
# outro bells + pad
def bell(f,dur=3.5):
    n=int(dur*SR); tt=np.arange(n)/SR
    return sum(g*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*d) for r,g,d in [(1,1,1.3),(2.76,.4,2.5),(5.4,.2,4),(.5,.3,1.)])
add(bell(329.63),-0.2,0.10,outro-0.2); add(bell(493.88),0.2,0.06,outro+1.8)
add(lp(saw(164.8)+saw(247.2),500)*env_seg(outro-0.3,T,1.2,0.8),0,0.04)
mus=np.stack([L,R],1); mus/=np.abs(mus).max(); mus*=0.9
sf.write("music.wav",mus.astype(np.float32),SR); print("music ok",T)
