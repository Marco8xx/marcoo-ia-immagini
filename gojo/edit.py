import math, random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont, ImageChops
random.seed(7)
SRC="gojo/originale.jpg"
S=2
im=Image.open(SRC).convert("RGB")
W,H=im.size[0]*S, im.size[1]*S
# --- quality: upscale, denoise JPEG artifacts, sharpen, local contrast
im=im.filter(ImageFilter.MedianFilter(3)) if False else im
im=im.resize((W,H),Image.LANCZOS)
im=im.filter(ImageFilter.UnsharpMask(radius=3,percent=90,threshold=2))
blur=im.filter(ImageFilter.GaussianBlur(40))
a=np.asarray(im).astype(np.float32); b=np.asarray(blur).astype(np.float32)
a=np.clip(a+(a-b)*0.18,0,255)          # local contrast (clarity)
im=Image.fromarray(a.astype(np.uint8))
im=ImageEnhance.Contrast(im).enhance(1.06)
im=im.filter(ImageFilter.UnsharpMask(radius=1.2,percent=70,threshold=1))
# boost cyan eyes glow
eyes=Image.new("L",(W,H),0); ImageDraw.Draw(eyes).ellipse((360*S,215*S,440*S,265*S),fill=255)
eyes=eyes.filter(ImageFilter.GaussianBlur(18*S))
glow=Image.new("RGB",(W,H),(90,220,255))
im=Image.composite(ImageChops.screen(im,glow),im,eyes.point(lambda v:int(v*0.45)))
# vignette
yy,xx=np.mgrid[0:H,0:W]; d=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H*0.45)/(H/2))**2)
v=np.clip(1-0.45*np.clip(d-0.55,0,1)**1.5,0,1)
im=Image.fromarray((np.asarray(im)*v[...,None]).astype(np.uint8))

# --- aggressive shout bubble
cx,cy,rx,ry=165*S,175*S,145*S,108*S
tip=(322*S,238*S)
pts=[]; n=26
for i in range(n*2):
    t=2*math.pi*i/(n*2)-math.pi/2
    r=1.0 if i%2==0 else random.uniform(0.70,0.80)
    if i%2==0: r*=random.uniform(1.0,1.22)
    pts.append((cx+rx*r*math.cos(t),cy+ry*r*math.sin(t)))
# tail: replace spikes near the tip direction
ang=math.atan2((tip[1]-cy)/ry,(tip[0]-cx)/rx)
def tail_poly(scale=1.0,off=0):
    base1=(cx+rx*0.80*math.cos(ang-0.22),cy+ry*0.80*math.sin(ang-0.22))
    base2=(cx+rx*0.80*math.cos(ang+0.22),cy+ry*0.80*math.sin(ang+0.22))
    mid=(tip[0]-28*S,tip[1]-22*S)
    return [base1,(mid[0]+14*S,mid[1]-10*S),tip,(mid[0]-8*S,mid[1]+18*S),base2]
layer=Image.new("RGBA",(W,H),(0,0,0,0)); dr=ImageDraw.Draw(layer)
# cyan cursed-energy aura + black outline + white fill
aura=Image.new("L",(W,H),0); ad=ImageDraw.Draw(aura)
ad.polygon(pts,fill=255); ad.polygon(tail_poly(),fill=255)
aura=aura.filter(ImageFilter.MaxFilter(21)).filter(ImageFilter.GaussianBlur(9*S))
im=Image.composite(Image.new("RGB",(W,H),(70,210,255)),im,aura.point(lambda v:int(v*0.85)))
outline=Image.new("L",(W,H),0); od=ImageDraw.Draw(outline)
od.polygon(pts,fill=255); od.polygon(tail_poly(),fill=255)
thick=outline.filter(ImageFilter.MaxFilter(21))
im.paste((0,0,0),mask=thick)
im.paste((255,255,255),mask=outline)
# inner speed/impact lines inside bubble edge
d2=ImageDraw.Draw(im)
for i in range(40):
    t=random.uniform(0,2*math.pi); r1=random.uniform(0.62,0.70); r2=r1+random.uniform(0.06,0.12)
    d2.line([(cx+rx*r1*math.cos(t),cy+ry*r1*math.sin(t)),(cx+rx*r2*math.cos(t),cy+ry*r2*math.sin(t))],fill=(20,20,20),width=2*S)
# --- text
F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def text_img(txt,size):
    f=ImageFont.truetype(F,size)
    bb=f.getbbox(txt); w,h=bb[2]-bb[0]+60,bb[3]-bb[1]+60
    t=Image.new("L",(w,h),0); ImageDraw.Draw(t).text((30-bb[0],30-bb[1]),txt,font=f,fill=255)
    t=t.transform((int(w*1.0),h),Image.AFFINE,(1,0.22,-0.22*h*0.5+0,0,1,0),Image.BICUBIC)  # italic shear
    return t
def place(txt,size,center,rot,stretch=1.35):
    global im
    m=text_img(txt,size); m=m.resize((m.width,int(m.height*stretch)),Image.LANCZOS)
    m=m.rotate(rot,Image.BICUBIC,expand=True)
    x,y=int(center[0]-m.width/2),int(center[1]-m.height/2)
    full=Image.new("L",(W,H),0); full.paste(m,(x,y))
    stroke=full.filter(ImageFilter.MaxFilter(9))
    shadow=Image.new("L",(W,H),0); shadow.paste(stroke,(10,12))
    im.paste((255,40,40),mask=shadow)       # red offset hit-shadow
    im.paste((0,0,0),mask=stroke)
    im.paste((0,0,0),mask=full)
place("NAH,",42*S,(cx-8*S,cy-48*S),8)
place("I'D WIN",54*S,(cx+6*S,cy+22*S),6)
d3=ImageDraw.Draw(im)
for x0,y0 in [(cx+118*S,cy-70*S),(cx+132*S,cy-40*S)]:
    pass
im=im.filter(ImageFilter.UnsharpMask(radius=0.8,percent=30,threshold=0))
out="gojo/gojo-nah-id-win.png"
im.save(out,optimize=True); im.convert("RGB").save(out.replace(".png",".jpg"),quality=95)
print(im.size)
