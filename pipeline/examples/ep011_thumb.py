import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
W,H=1080,1920
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
k=(yy/H)[...,None]; bg=np.array([8,30,46])*(1-k)+np.array([0,3,8])*k
img=Image.fromarray(bg.clip(0,255).astype(np.uint8)); d=ImageDraw.Draw(img)
rng=np.random.default_rng(2)
for _ in range(260):
    x,y,r=rng.uniform(0,W),rng.uniform(0,H),rng.uniform(1,5); a=int(rng.uniform(60,170)); d.ellipse((x-r,y-r,x+r,y+r),fill=(a//2,a,a))
pts=[]; cx,cy,wd,amp=540,1080,980,300
for i in range(320):
    u=i/319; x=cx-wd/2+u*wd; env=math.sin(math.pi*u)**1.5; pts.append((x,cy-amp*env*math.sin(2*math.pi*(6+18*u)*u)))
glow=Image.new("RGB",(W,H)); ImageDraw.Draw(glow).line(pts,fill=(60,200,255),width=56); glow=glow.filter(ImageFilter.GaussianBlur(30))
img=ImageChops.screen(img,glow); img=ImageChops.screen(img,glow); ImageDraw.Draw(img).line(pts,fill=(215,250,255),width=8)
a=np.asarray(img,np.float32); v=(1-0.7*(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.62))**2)).clip(0.25,1)[...,None]
img=Image.fromarray((a*v).clip(0,255).astype(np.uint8)).convert("RGBA"); d=ImageDraw.Draw(img)
F=lambda s: ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf",s)
def c(y,s,f,col):
    b=d.textbbox((0,0),s,font=f); d.text(((W-(b[2]-b[0]))//2,y),s,font=f,fill=col,stroke_width=8,stroke_fill=(0,0,0))
c(250,"THE OCEAN SOUND",F(120),(245,245,240))
c(400,"NEVER",F(230),(255,64,64))
c(640,"SOLVED",F(230),(255,64,64))
fs=ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf",46)
b=d.textbbox((0,0),"EP 011 · SINCE 1991",font=fs); w=b[2]-b[0]
d.rounded_rectangle(((W-w)//2-30,1440,(W+w)//2+30,1520),radius=14,fill=(255,181,71))
d.text(((W-w)//2,1452),"EP 011 · SINCE 1991",font=fs,fill=(10,10,10))
img.convert("RGB").save("thumb_ep011_9x16.jpg",quality=92); print("ok")
