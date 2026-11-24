exec(open('render.py').read().split('def frame')[0])
t=2.0; arr=np.zeros((H,W,3),np.float32); img=Image.new("RGBA",(W,H),(0,0,0,0))
thermal_bg(arr,t,70,26); ir_object(arr,t,540,1000,260)
arr*=VIG; base=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)).convert("RGBA")
hud(base,t,(540,1080,330),zoomtxt="x24.0",clock0=37000)
d=ImageDraw.Draw(base)
def c(y,s,f,col):
    b=d.textbbox((0,0),s,font=f); d.text(((W-(b[2]-b[0]))//2,y),s,font=f,fill=col,stroke_width=9,stroke_fill=(0,0,0))
c(250,"THE MILITARY FILMED",font(FONT_BIG,104),WHITE)
c(380,"A JELLYFISH",font(FONT_BIG,190),AMBER)
c(1530,"IN THE SKY",font(FONT_BIG,170),RED)
fs=font(FONT_SMB,46); s="EP 012 · IRAQ 2017"; b=d.textbbox((0,0),s,font=fs); w=b[2]-b[0]
d.rounded_rectangle(((W-w)//2-30,1760,(W+w)//2+30,1840),radius=14,fill=AMBER+(255,)); d.text(((W-w)//2,1772),s,font=fs,fill=(10,10,10))
base.convert("RGB").save("thumb_ep012_9x16.jpg",quality=90); print("ok")
