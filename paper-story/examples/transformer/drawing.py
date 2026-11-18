"""前向演示绘图基础：只使用 Pillow CPU。"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['OMP_NUM_THREADS']='2'
from pathlib import Path
from functools import lru_cache
import json,math,subprocess,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=Path(__file__).resolve().parent
W,H,FPS=1600,900,25
BG='#f3f0e8';INK='#262b29';MUTED='#747b73';ORANGE='#e97650';SAGE='#b2c2a7';BLUE='#b5c9dc';PURPLE='#c1b6da';LINE='#d8d9ce';WHITE='#fffdf8'
DATA=json.loads((P/'storyboard.json').read_text())
TIMELINE=json.loads((P/'timeline.json').read_text())
DURATION=TIMELINE['duration']
@lru_cache(maxsize=150)
def font(size,bold=False):
 return ImageFont.truetype(str(P/'assets'/('NotoSansSC-Bold.ttf' if bold else 'NotoSansSC-Regular.ttf')),size)
@lru_cache(maxsize=1800)
def glyph(s,size,color,bold=False):
 f=font(size,bold);b=f.getbbox(s);im=Image.new('RGBA',(max(1,int(f.getlength(s))+4),size*2),(0,0,0,0));d=ImageDraw.Draw(im);d.text((0,-b[1]),s,font=f,fill=color)
 return im.crop((0,0,im.width,max(1,b[3]-b[1]+3)))
def text(im,s,x,y,size=30,color=INK,bold=False,center=False,alpha=1):
 t=glyph(str(s),size,color,bold)
 if center:x-=t.width/2
 if alpha<1:t=t.copy();t.putalpha(t.getchannel('A').point(lambda v:int(v*max(0,alpha))))
 im.paste(t,(round(x),round(y)),t)
def rr(d,box,fill=WHITE,outline=None,r=24,width=2):d.rounded_rectangle(tuple(round(x) for x in box),r,fill=fill,outline=outline,width=width)
def ease(p):p=max(0,min(1,p));return 1-(1-p)**3
def lerp(a,b,p):return a+(b-a)*p
def arrow(d,x1,y1,x2,y2,color=INK,width=4,p=1):
 x2=lerp(x1,x2,p);y2=lerp(y1,y2,p);d.line((x1,y1,x2,y2),fill=color,width=width)
 a=math.atan2(y2-y1,x2-x1);l=13;d.polygon([(x2,y2),(x2-l*math.cos(a-.5),y2-l*math.sin(a-.5)),(x2-l*math.cos(a+.5),y2-l*math.sin(a+.5))],fill=color)
def curve(d,a,b,c,color=INK,width=3,p=1):
 pts=[]
 for i in range(max(2,int(60*p))):
  t=i/59;pts.append(((1-t)**2*a[0]+2*(1-t)*t*b[0]+t*t*c[0],(1-t)**2*a[1]+2*(1-t)*t*b[1]+t*t*c[1]))
 if len(pts)>1:d.line(pts,fill=color,width=width)
def chip(im,label,x,y,fill=SAGE,fg=INK,size=24,pad=18):
 width=glyph(label,size,fg,True).width+pad*2;d=ImageDraw.Draw(im);rr(d,(x,y,x+width,y+size+22),fill,r=18);text(im,label,x+pad,y+9,size,fg,True);return width

def eyes(d,x,y,t,scale=1):
 blink=1 if math.sin(t*1.7)>.98 else 8*scale
 for xx in [x-14*scale,x+14*scale]:d.ellipse((xx-4*scale,y-blink/2,xx+4*scale,y+blink/2),fill=INK)
 d.arc((x-12*scale,y+3*scale,x+12*scale,y+20*scale),0,180,fill=INK,width=2)
def paper(im,x,y,w,h,t,color=WHITE,title=True):
 d=ImageDraw.Draw(im);rr(d,(x+10,y+13,x+w+10,y+h+13),'#dddcd2',r=24);rr(d,(x,y,x+w,y+h),color,INK,24,3)
 if title:
  text(im,'Attention Is',x+30,y+42,34,INK,True);text(im,'All You Need',x+30,y+90,34,INK,True)
  text(im,'Vaswani et al. · 2017',x+30,y+152,20,MUTED)
  for j,l in enumerate([.8,.9,.62,.86]):d.line((x+30,y+205+j*22,x+w*l,y+205+j*22),fill=LINE,width=4)
 eyes(d,x+w/2,y+h-55,t,1.5)
