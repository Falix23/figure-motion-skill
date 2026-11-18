"""完整论文故事：背景、主张、结构与前向、实验和开放问题。纯 CPU。"""
from drawing import *
import technical as tech
N=len(DATA['scenes'])

def phase(i,gt):
 us=[u for u in TIMELINE['utterances'] if u['scene']==i]
 j=0 if gt<us[1]['start'] else 1;u=us[j]
 return j,max(0,min(1,(gt-u['start'])/(u['end']-u['start'])))

def base(i,gt):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 for x in range(24,W,40):
  for y in range(20,H,40):d.ellipse((x,y,x+1,y+1),fill='#e3e3d8')
 text(im,'PAPER / STORY',70,40,23,INK,True)
 text(im,'Transformer · 从论文背景到一次前向',353,42,21,MUTED)
 text(im,f'{i+1:02d} / {N:02d}',1405,42,22,MUTED)
 s=DATA['scenes'][i];text(im,s['label'],70,99,22,ORANGE,True)
 text(im,s['title'],70,146,49,INK,True)
 note='原文依据：Vaswani et al., 2017 · Attention Is All You Need'
 if 3<=i<11:note='教学简化 · 权重和概率非模型实测 · 原文 §3 / Fig.1'
 if i==11:note='原文 §6.1 / Table 2 · 同一表列出的英译德测试成绩及估算 FLOPs'
 if i==12:note='原文 §4 / Table 1 · 展示原始全注意力分数矩阵；末句为讲解延伸问题'
 text(im,note,70,850,15,MUTED)
 sw=(1460-(N-1)*7)/N
 for j,z in enumerate(TIMELINE['scenes']):
  x=70+j*(sw+7);rr(d,(x,878,x+sw,883),LINE,r=2)
  q=max(0,min(1,(gt-z['start'])/(z['end']-z['start'])))
  if q:rr(d,(x,878,x+max(1,sw*q),883),ORANGE,r=2)
 return im
tech.base=lambda i,gt:base(i+3,gt)

def subtitle(im,gt):
 d=ImageDraw.Draw(im);sub=next((u['text'] for u in TIMELINE.get('captions',TIMELINE['utterances']) if u['start']<=gt<u['end']),None)
 if not sub:return
 lines=[];line=''
 for c in sub:
  if glyph(line+c,29,WHITE).width>1390:lines.append(line);line=c
  else:line+=c
 if line:lines.append(line)
 y=799-36*(len(lines)-1);rr(d,(60,y-12,1540,y+36*len(lines)+6),INK,r=14)
 for j,line in enumerate(lines):text(im,line,800,y+j*36,29,WHITE,False,True)

def custom(i,gt):
 im=base(i,gt);d=ImageDraw.Draw(im);z=TIMELINE['scenes'][i];t=gt-z['start'];k,u=phase(i,gt)
 if i==0:
  chip(im,'机器翻译 / MACHINE TRANSLATION',80,250,BLUE,INK,24)
  text(im,'一种语言，怎样准确变成另一种？',85,340,36,INK,True)
  tech.node(im,'我爱你',90,429,290,85,SAGE,43)
  arrow(d,400,471,495,471,ORANGE,5,ease(t/1.5))
  tech.node(im,'I love you',520,429,330,85,PURPLE,42)
  chip(im,'更准确',128,594,SAGE,INK,29);chip(im,'训练更高效',490,594,BLUE,INK,29)
  paper(im,1045,271+math.sin(t*.9)*4,390,431,t)
  if k==1:chip(im,'标题很大胆，目标很实际。',892,719,ORANGE,WHITE,24)
  else:text(im,'研究目标：质量与训练效率',87,722,27,MUTED)
 elif i==1:
  text(im,'循环网络：沿着句子，逐步更新表示',80,244,30,MUTED)
  xs=[115+231*j for j in range(6)];y=415
  for j,x in enumerate(xs):
   tech.node(im,'位置 '+str(j+1),x,y,190,78,BLUE if j in [0,5] else WHITE,30)
   if j<5:arrow(d,x+200,y+39,x+220,y+39,MUTED,3)
  path=[(xs[0]+95,y+39)]+[(x+95,y+39) for x in xs[1:]]
  tech.dot_path(d,path,t,ORANGE,10,4)
  curve(d,(xs[0]+95,y-16),(800,286),(xs[-1]+95,y-16),ORANGE,3,ease(t/2))
  text(im,'远处的信息，需要跨越多个计算步骤',800,321,28,ORANGE,True,True)
  for x,w,title,sub in [(90,690,'长距离联系','传递路径更长'),(840,670,'句内并行','受前一步计算依赖限制')]:
   rr(d,(x,568,x+w,696),SAGE if x==90 else PURPLE,INK,24,2)
   text(im,title,x+31,590,30,INK,True);text(im,sub,x+31,644,25,INK)
  text(im,'这里解释循环计算的限制；此前也存在卷积等其他路线',800,721,20,MUTED,False,True)
 elif i==2:
  text(im,'已有注意力 → 用注意力组织整个架构',80,244,30,MUTED)
  rr(d,(100,390,484,594),WHITE,INK,24,2)
  text(im,'已有的注意力机制',292,428,32,INK,True,True)
  text(im,'常与循环网络结合',292,511,25,MUTED,False,True)
  arrow(d,507,490,590,490,ORANGE,5,ease(t/2))
  cx,cy,r=834,479,123;positions=[]
  for j in range(6):
   a=2*math.pi*j/6;positions.append((cx+r*math.cos(a),cy+r*math.sin(a)))
  for j,a in enumerate(positions):
   for b in positions[j+1:]:d.line((*a,*b),fill=LINE,width=2)
  for j,(x,y) in enumerate(positions):
   d.ellipse((x-17,y-17,x+17,y+17),fill=[BLUE,SAGE,PURPLE][j%3],outline=INK,width=2)
  rr(d,(721,440,947,518),SAGE,INK,16,2);text(im,'注意力为核心',834,464,29,INK,True,True)
  arrow(d,1013,490,1094,490,ORANGE,5,ease((t-1)/2))
  rr(d,(1120,368,1506,614),WHITE,INK,24,2)
  text(im,'Transformer',1313,401,36,INK,True,True)
  tech.node(im,'编码器',1156,478,143,65,SAGE,25);tech.node(im,'解码器',1324,478,143,65,PURPLE,25)
  text(im,'完整的序列转换架构',1313,568,23,MUTED,False,True)
  chip(im,'接下来：跟着一句话，走一遍。',555,701,ORANGE,WHITE,27)
 elif i==11:
  text(im,'WMT 2014 · 英语 → 德语',80,244,30,MUTED)
  rr(d,(80,325,785,693),WHITE,INK,25,2);rr(d,(840,325,1520,693),WHITE,INK,25,2)
  text(im,'翻译质量 / BLEU ↑',114,350,29,INK,True)
  text(im,'估算训练计算量 / FLOPs ↓',875,350,28,INK,True)
  leftp=ease(t/3);rightp=ease(t/3)
  for j,(name,score,col) in enumerate([('此前最佳集成',26.36,BLUE),('Transformer big',28.4,SAGE)]):
   yy=410+j*131;text(im,name,116,yy,25,INK,True)
   ww=score/32*540*leftp;rr(d,(116,yy+42,116+max(1,ww),yy+80),col,r=8)
   text(im,f'{score:.2f}',681,yy+40,29,INK,True)
  for j,(name,value,col) in enumerate([('此前最佳集成',7.7,BLUE),('Transformer big',2.3,SAGE)]):
   yy=410+j*131;text(im,name,876,yy,25,INK,True)
   ww=value/7.7*400*rightp;rr(d,(876,yy+42,876+max(1,ww),yy+80),col,r=8)
   text(im,str(value)+'e19',1310,yy+40,28,INK,True)
  text(im,'此前最佳集成 = ConvS2S Ensemble；FLOPs 为论文估算，非本片实测',800,721,21,MUTED,False,True)
 elif i==12:
  text(im,'原始全注意力：每个位置，匹配所有位置',80,244,30,MUTED)
  for j,(n,x) in enumerate([(4,170),(8,660),(16,1150)]):
   cell=265/n;yy=361
   reveal=1 if j==0 else (ease((u-(j-1)*.24)*4) if k==1 else 0)
   text(im,'n = '+str(n),x+132,306,31,INK,True,True)
   for rr0 in range(n):
    for cc in range(n):
     xx=x+cc*cell;y0=yy+rr0*cell;filled=(rr0*n+cc)<n*n*reveal
     col=[BLUE,SAGE,PURPLE][j] if filled else WHITE
     rr(d,(xx+1,y0+1,xx+cell-2,y0+cell-2),col,LINE,2,1)
   text(im,str(n*n)+' 个分数',x+132,646,27,INK,True,True)
  rr(d,(180,680,1420,739),WHITE,INK,17,2)
  text(im,'怎样保留全局联系，又减少开销？',800,696,34,INK,True,True)
 subtitle(im,gt);return im

def frame(gt):
 i=next((i for i,z in enumerate(TIMELINE['scenes']) if z['start']<=gt<z['end']),N-1)
 im=tech.paint(i-3,gt) if 3<=i<11 else custom(i,gt)
 z=TIMELINE['scenes'][i];f=min(1,max(0,(gt-z['start'])/.18),max(0,(z['end']-gt)/.18))
 return Image.blend(Image.new('RGB',(W,H),BG),im,f) if f<1 else im

def run():
 ff=imageio_ffmpeg.get_ffmpeg_exe();out=P/'transformer_story.mp4'
 cmd=[ff,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(P/'narration.wav'),'-c:v','libx264','-preset','fast','-crf','19','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-shortest',str(out)]
 with (P/'encode.log').open('w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for n in range(math.ceil(DURATION*FPS)):
   proc.stdin.write(frame(n/FPS).tobytes())
   if n%(FPS*10)==0:print('render',round(n/FPS,1),'/',round(DURATION,1),flush=True)
  proc.stdin.close();code=proc.wait()
  if code:raise RuntimeError('encode failed '+str(code))
 print('VIDEO_READY',out,flush=True)
if __name__=='__main__':
 if '--stills' in sys.argv:
  for i,z in enumerate(TIMELINE['scenes']):
   us=[u for u in TIMELINE['utterances'] if u['scene']==i]
   for j,u in enumerate(us):frame(u['start']+(u['end']-u['start'])*.7).save(P/f'preview_{i:02}_{j}.jpg',quality=94)
 else:run()
