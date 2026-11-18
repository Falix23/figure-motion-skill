"""原始 Transformer 整体结构和教学前向过程；纯 CPU 绘图与编码。"""
from drawing import *
FULL_DATA=DATA
FULL_TIMELINE=TIMELINE
DATA={**FULL_DATA,'scenes':FULL_DATA['scenes'][3:11]}
TIMELINE={**FULL_TIMELINE,'scenes':FULL_TIMELINE['scenes'][3:11], 'utterances':[{**u,'scene':u['scene']-3} for u in FULL_TIMELINE['utterances'] if 3<=u['scene']<11], 'captions':[{**u,'scene':u['scene']-3} for u in FULL_TIMELINE.get('captions',FULL_TIMELINE['utterances']) if 3<=u['scene']<11]}
TOY=json.loads((P/'toy_attention.json').read_text())
N=len(DATA['scenes'])
def phase(i,gt):
 us=[u for u in TIMELINE['utterances'] if u['scene']==i]
 idx=0 if gt<us[1]['start'] else 1
 u=us[idx];return idx,max(0,min(1,(gt-u['start'])/(u['end']-u['start'])))
def node(im,label,x,y,w=320,h=44,col=WHITE,sz=23,active=False):
 d=ImageDraw.Draw(im);rr(d,(x,y,x+w,y+h),col,ORANGE if active else INK,12,4 if active else 2)
 text(im,label,x+w/2,y+(h-glyph(label,sz,INK,True).height)/2,sz,INK,True,True)
def dot_path(d,pts,t,col=ORANGE,r=8,period=2.2):
 lengths=[math.dist(a,b) for a,b in zip(pts,pts[1:])];total=sum(lengths)
 if not total:return
 for offset in [0,.35]:
  dst=((t/period+offset)%1)*total
  for a,b,length in zip(pts,pts[1:],lengths):
   if dst<=length:
    q=dst/length;x=lerp(a[0],b[0],q);y=lerp(a[1],b[1],q);d.ellipse((x-r,y-r,x+r,y+r),fill=col);break
   dst-=length

def label_box(im,label,x,y,w,col=WHITE,h=55,size=27):node(im,label,x,y,w,h,col,size)
def vector(im,x,y,vals,col=SAGE,w=145,h=94,p=1):
 d=ImageDraw.Draw(im);rr(d,(x,y,x+w,y+h),WHITE,INK,14,2)
 for j,v in enumerate(vals):
  yy=y+14+j*23;d.line((x+18,yy+7,x+w-18,yy+7),fill=LINE,width=3)
  ww=(w-37)*abs(v)*p;rr(d,(x+18,yy,x+18+max(1,ww),yy+14),col,r=4)

def structure(im,gt,recap=False):
 d=ImageDraw.Draw(im)
 for x,label,col in [(215,'编码器',SAGE),(930,'解码器',PURPLE)]:
  chip(im,label,x+102,267,col,INK,25)
 rr(d,(215,420,690,622),WHITE,LINE,18,2);rr(d,(930,348,1405,622),WHITE,LINE,18,2)
 text(im,'× 6 层',630,430,18,MUTED,True);text(im,'× 6 层',1341,354,18,MUTED,True)
 # 自下而上的 Post-LN 原始结构。
 d.line((419,652,419,454),fill=INK,width=3);d.line((1134,652,1134,315),fill=INK,width=3)
 for label,y,col in [('多头自注意力',567,SAGE),('前馈网络',491,SAGE)]:
  node(im,label,248,y,342,40,col,23)
  node(im,'Add & Norm',248,y-29,342,22,WHITE,15)
  arrow(d,419,y-3,419,y-7,INK,2)
  d.line((419,y+46,628,y+46,628,y-18,599,y-18),fill='#77948b',width=2)
  text(im,'+',604,y-27,21,MUTED)
 arrow(d,419,533,419,531,INK,2)
 for label,y,col in [('带掩码的自注意力',567,PURPLE),('交叉注意力',489,BLUE),('前馈网络',411,PURPLE)]:
  node(im,label,963,y,342,40,col,22)
  node(im,'Add & Norm',963,y-29,342,22,WHITE,15)
  d.line((1134,y+46,1354,y+46,1354,y-18,1314,y-18),fill='#8e80a7',width=2)
  text(im,'+',1319,y-27,21,MUTED)
 # 编码上下文直达每个解码层的交叉注意力。
 route=[(419,454),(419,340),(795,340),(795,509),(951,509)]
 d.line(route,fill='#708e8d',width=4);arrow(d,915,509,951,509,'#708e8d',4)
 text(im,'编码器输出',628,353,20,MUTED,False,True)
 for x in [248,963]:
  node(im,'词嵌入 + 位置编码',x,652,342,42,BLUE if x==248 else PURPLE,22)
  arrow(d,x+171,643,x+171,619,INK,3)
 text(im,'我     爱     你',419,714,28,INK,True,True)
 text(im,'<BOS>     I',1134,714,27,INK,True,True)
 arrow(d,419,703,419,697,INK,3);arrow(d,1134,703,1134,697,INK,3)
 node(im,'线性层 → softmax',963,317,342,27,ORANGE,18)
 arrow(d,1134,375,1134,351,INK,3)
 text(im,'下一词概率',1454,324,20,INK,False,True)
 arrow(d,1316,331,1370,331,ORANGE,3)
 if recap:
  for pts,col in [([(419,706),(419,630),(419,454)],SAGE),(route,BLUE),([(1134,706),(1134,630),(1134,375),(1134,315)],ORANGE)]:dot_path(d,pts,gt,col,7)
  text(im,'训练：多个位置并行计算（仍有因果掩码）   ·   生成：前缀逐步增长',800,760,22,MUTED,False,True)
 else:
  dot_path(d,[(419,706),(419,630),(419,454)],gt,SAGE,7)
  dot_path(d,[(1134,706),(1134,630),(1134,375),(1134,315)],gt,ORANGE,7)
  text(im,'沿箭头自下而上读 · Add & Norm = 残差相加 + 层归一化',800,760,22,MUTED,False,True)

def minimap(im,focus,gt):
 d=ImageDraw.Draw(im);rr(d,(44,273,355,746),WHITE,LINE,22,2)
 text(im,'结构小地图',70,294,21,MUTED,True)
 text(im,'编码器',131,347,21,INK,True,True);text(im,'解码器',277,347,21,INK,True,True)
 enc=[('前馈',418,'ffn'),('自注意力',496,'self'),('向量 + 位置',634,'embed')]
 dec=[('概率输出',384,'head'),('前馈',434,'dffn'),('交叉注意力',496,'cross'),('带掩码',558,'mask'),('向量 + 位置',634,'prefix')]
 for x,items,col in [(71,enc,SAGE),(216,dec,PURPLE)]:
  for lab,y,key in items:node(im,lab,x,y,119,38,col,17,key in focus)
  ys=sorted([y for _,y,_ in items],reverse=True)
  for a,b in zip(ys,ys[1:]):
   xx=x+59;yy=b+41;d.line((xx,a-3,xx,yy),fill=MUTED,width=2);d.polygon([(xx,yy),(xx-4,yy+6),(xx+4,yy+6)],fill=MUTED)
 pts=[(131,408),(131,389),(202,389),(202,515),(212,515)]
 d.line(pts,fill='#819f94',width=2)
 if 'cross' in focus:dot_path(d,pts,gt,ORANGE,4,1.7)
 text(im,'原文',130,690,18,MUTED,False,True);text(im,'已知前缀',275,690,18,MUTED,False,True)
 text(im,'各子层后均有 Add & Norm',200,720,15,MUTED,False,True)

def base(i,gt):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 for x in range(24,W,40):
  for y in range(20,H,40):d.ellipse((x,y,x+1,y+1),fill='#e3e3d8')
 text(im,'PAPER / STORY',70,40,23,INK,True);text(im,'Transformer · 结构与前向',353,42,21,MUTED)
 text(im,f'{i+1:02d} / {N:02d}',1405,42,22,MUTED)
 s=DATA['scenes'][i];text(im,s['label'],70,99,22,ORANGE,True)
 text(im,s['title'],70,146,49,INK,True)
 text(im,'教学简化 · 权重和概率非模型实测 · 依据原文 §3 / Fig.1',70,850,15,MUTED)
 segw=(1460-7*8)/8
 for j,z in enumerate(TIMELINE['scenes']):
  x=70+j*(segw+8);rr(d,(x,878,x+segw,883),LINE,r=2)
  q=max(0,min(1,(gt-z['start'])/(z['end']-z['start'])))
  if q:rr(d,(x,878,x+max(1,segw*q),883),ORANGE,r=2)
 return im

def paint(i,gt):
 im=base(i,gt);d=ImageDraw.Draw(im);s=TIMELINE['scenes'][i];t=gt-s['start'];k,u=phase(i,gt)
 if i in [0,7]:
  text(im,'原始论文的编码器—解码器结构',72,218,25,MUTED)
  structure(im,t,i==7)
 else:
  focuses={1:['embed'],2:['self'],3:['self'],4:['ffn'],5:['mask'] if k==0 else ['cross'],6:['head','dffn'] if k==0 else ['prefix','head']}
  minimap(im,focuses[i],t)
  d.line((385,277,385,745),fill=LINE,width=2)
 if i==1:
  text(im,'同一句话，变成可计算的表示',430,249,27,MUTED)
  for j,(x,word,col) in enumerate([(525,'我',BLUE),(895,'爱',SAGE),(1265,'你',PURPLE)]):
   node(im,word,x,329,180,72,col,39)
   q=ease((t-1-j*.15)/1.2);arrow(d,x+90,414,x+90,470,INK,4,q)
   vector(im,x+17,487,[[.3,.8,.4],[.7,.4,.9],[.4,.6,.8]][j],col,p=q)
   if k==1:
    v=ease(u*2.7);chip(im,'+ 位置 '+str(j+1),x-4,609,ORANGE,WHITE,23)
    arrow(d,x+90,591,x+90,603,ORANGE,3,v)
    text(im,'词义 + 顺序',x+90,696,25,INK,True,True)
  text(im,'向量的条形显示仅作示意',975,745,20,MUTED,False,True)
 elif i==2:
  text(im,'同一组输入，投影出查询、键和值',430,249,27,MUTED)
  for j,(x,word,col) in enumerate([(520,'我',BLUE),(900,'爱',SAGE),(1280,'你',PURPLE)]):
   node(im,word,x,320,140,64,col,34)
  if k==0:
   for j,(x,col) in enumerate([(590,BLUE),(970,SAGE),(1350,PURPLE)]):
    pts=[(x,394),(x,465),(970,598)]
    d.line(pts,fill=col,width=5);dot_path(d,pts,t+j*.5,col,9)
   node(im,'爱：汇合上下文后的新表示',725,602,495,70,SAGE,27)
   text(im,'每个位置都这样计算；这里聚焦“爱”',975,717,24,MUTED,False,True)
  else:
   for lab,x,col,sub in [('Q 查询',475,ORANGE,'想找什么'),('K 键',835,BLUE,'用来匹配'),('V 值',1195,SAGE,'提供内容')]:
    node(im,lab,x,456,260,76,col,31);text(im,sub,x+130,550,23,MUTED,False,True)
   # 同一组输入分叉成三套投影，避免误画成三个词各自产生 Q/K/V。
   d.line((590,396,590,423,1350,423,1350,396),fill=MUTED,width=3)
   d.line((970,396,970,423),fill=MUTED,width=3)
   for x in [605,965,1325]:arrow(d,x,425,x,443,MUTED,3,ease(u*4))
   d.line((605,591,605,629,965,629,965,591),fill=INK,width=3)
   node(im,'缩放点积 → softmax → 权重',625,646,640,58,WHITE,27)
   arrow(d,1325,595,1325,675,SAGE,4,ease((u-.3)*4))
   text(im,'再与 V 加权汇合',1325,720,22,INK,False,True)
 elif i==3:
  if k==0:
   text(im,'仅演示“爱”这个位置的一次单头计算',430,249,26,MUTED)
   for j,(x,word,col,v,w) in enumerate([(520,'我',BLUE,'[1, 0]','0.20'),(875,'爱',SAGE,'[0, 1]','0.50'),(1230,'你',PURPLE,'[1, 1]','0.30')]):
    node(im,word,x,318,170,56,col,33)
    text(im,'V = '+v,x+85,406,28,INK,True,True)
    chip(im,w,x+40,458,col,INK,25)
    route=[(x+85,517),(x+85,550),(960,620)]
    d.line(route,fill=col,width=3+2*j);dot_path(d,route,t+j*.3,col,7+j,2.1)
   node(im,'新表示 [0.50, 0.80]',716,620,490,65,ORANGE,32)
   text(im,'0.2[1,0] + 0.5[0,1] + 0.3[1,1] = [0.5,0.8]',960,724,27,INK,False,True)
  else:
   text(im,'刚才的单头结果，是多头输出中的一份',430,249,26,MUTED)
   for j,(y,col) in enumerate([(345,BLUE),(487,SAGE),(629,PURPLE)]):
    node(im,'头 '+str(j+1),465,y,230,64,col,32)
    route=[(709,y+32),(790,y+32),(900,519)]
    d.line(route,fill=col,width=4);dot_path(d,route,t+j*.3,col,9,1.7)
   node(im,'拼接',904,478,220,82,WHITE,34)
   arrow(d,1136,519,1190,519,ORANGE,5,ease(u*3))
   node(im,'输出投影',1204,478,285,82,ORANGE,32)
   text(im,'W_O',1346,597,31,MUTED,True,True)
   text(im,'图中只画 3 头；原文基础模型使用 8 头',960,733,23,MUTED,False,True)
 elif i==4:
  if k==0:
   text(im,'同一前馈网络，分别处理每个位置',430,249,27,MUTED)
   for j,(x,col) in enumerate([(478,BLUE),(848,SAGE),(1218,PURPLE)]):
    vector(im,x+62,324,[.4,.8,.5],col)
    arrow(d,x+134,432,x+134,478,INK,4)
    node(im,'前馈网络',x,491,270,67,WHITE,29)
    arrow(d,x+134,570,x+134,606,INK,4)
    vector(im,x+62,620,[.8,.3,.7],col,p=ease(u*2.5))
    dot_path(d,[(x+134,434),(x+134,480)],t+j*.25,col,8)
   text(im,'各位置独立计算，共享这一层的前馈参数',960,739,22,MUTED,False,True)
  else:
   text(im,'每个子层后：先残差相加，再层归一化',430,249,26,MUTED)
   for y,lab,col in [(330,'输入 x',BLUE),(438,'子层 f(x)',SAGE),(546,'相加：x + f(x)',WHITE),(654,'LayerNorm',PURPLE)]:node(im,lab,620,y,420,56,col,27)
   for y in [398,506,614]:arrow(d,830,y-5,830,y+24,INK,3)
   path=[(1050,358),(1160,358),(1160,574),(1050,574)]
   d.line(path,fill=ORANGE,width=4);arrow(d,1100,574,1050,574,ORANGE,4);dot_path(d,path,t,ORANGE,7,2)
   text(im,'保留输入',1178,451,23,ORANGE,True)
   for j in range(6):rr(d,(1380,340+j*49,1470,374+j*49),SAGE,INK,7,2)
   text(im,'× 6 层',1425,671,25,INK,True,True)
   text(im,'原始论文为 Post-LN；注意力与前馈各有一组 Add & Norm',960,741,20,MUTED,False,True)
 elif i==5:
  if k==0:
   text(im,'已知目标前缀：<BOS> I',430,249,27,MUTED)
   for j,(x,lab,col) in enumerate([(540,'<BOS>',PURPLE),(835,'I',PURPLE),(1130,'love（未来）',LINE)]):
    node(im,lab,x,318,230,61,col,29)
   text(im,'因果掩码',1040,463,34,INK,True)
   text(im,'挡住未来，不能偷看',1040,526,25,MUTED)
   labels=['<BOS>','I','love'];cx,cy,cell=610,458,71
   for r,lab in enumerate(labels):
    text(im,lab,cx-55,cy+r*cell+21,21,INK,False,True)
    text(im,lab,cx+r*cell+cell/2,cy-37,21,INK,False,True)
    for c in range(3):
     xx=cx+c*cell;yy=cy+r*cell;allowed=c<=r
     rr(d,(xx,yy,xx+cell-7,yy+cell-7),SAGE if allowed else LINE,ORANGE if r==1 else None,7,3)
     if not allowed:
      d.line((xx+22,yy+20,xx+43,yy+43),fill=MUTED,width=2);d.line((xx+43,yy+20,xx+22,yy+43),fill=MUTED,width=2)
   text(im,'未来行未计算',1030,638,23,MUTED)
   text(im,'本轮计算 I 行，只能查看 <BOS> 和 I',965,724,25,INK,False,True)
  else:
   text(im,'交叉注意力：解码器查询编码器的上下文',430,249,26,MUTED)
   node(im,'编码器输出',470,368,330,72,SAGE,31)
   node(im,'解码器当前表示',1100,368,370,72,PURPLE,30)
   node(im,'K / V',495,507,280,62,SAGE,29);node(im,'Q',1145,507,280,62,PURPLE,29)
   for x,col in [(635,SAGE),(1285,PURPLE)]:arrow(d,x,454,x,493,col,4)
   for pts,col in [([(635,583),(635,652),(935,652)],SAGE),([(1285,583),(1285,652),(1050,652)],PURPLE)]:
    d.line(pts,fill=col,width=5);dot_path(d,pts,t,col,9,1.9)
   node(im,'交叉注意力',900,611,290,84,BLUE,31)
   text(im,'Q 来自解码器；K、V 来自编码器',960,740,24,MUTED,False,True)
 elif i==6:
  text(im,'已有前缀 <BOS> I；本轮预测 love',430,249,26,MUTED)
  for j,(x,lab,col,sz) in enumerate([(430,'前馈 + Add & Norm',PURPLE,23),(805,'线性层',WHITE,32),(1180,'softmax',ORANGE,34)]):
   node(im,lab,x,345,310,79,col,sz)
   if j<2:arrow(d,x+321,385,x+362,385,INK,4,ease(t/2))
  for j,(label,prob,col) in enumerate([('love',.65,ORANGE),('like',.22,BLUE),('see',.13,LINE)]):
   y=505+j*69;text(im,label,469,y+6,29,INK,True)
   ww=prob*440*ease(t/2)
   rr(d,(573,y,573+max(1,ww),y+40),col,r=8)
   text(im,f'{prob:.0%}',1050,y+5,27,INK)
  text(im,'概率仅为教学示意',768,723,22,MUTED,False,True)
  node(im,'I',1200,508,105,69,PURPLE,36)
  if k==1:
   node(im,'love',1320,508,184,69,ORANGE,36,True)
   text(im,'新词接回解码器前缀',1335,613,25,INK,True,True)
   path=[(1410,591),(1410,697),(1160,697),(1160,475),(1230,475)]
   d.line(path,fill=ORANGE,width=4);dot_path(d,path,t,ORANGE,8,2.2)
 # 字幕单独占据底部安全区域。
 sub=next((z['text'] for z in TIMELINE.get('captions',TIMELINE['utterances']) if z['start']<=gt<z['end']),None)
 if sub:
  lines=[];line=''
  for c in sub:
   if glyph(line+c,29,WHITE).width>1390:lines.append(line);line=c
   else:line+=c
  if line:lines.append(line)
  y=799-36*(len(lines)-1);rr(d,(60,y-12,1540,y+36*len(lines)+6),INK,r=14)
  for j,line in enumerate(lines):text(im,line,800,y+j*36,29,WHITE,False,True)
 return im

def frame(gt):
 i=next((i for i,z in enumerate(TIMELINE['scenes']) if z['start']<=gt<z['end']),N-1)
 z=TIMELINE['scenes'][i];im=paint(i,gt)
 f=min(1,max(0,(gt-z['start'])/.16),max(0,(z['end']-gt)/.16))
 return Image.blend(Image.new('RGB',(W,H),BG),im,f) if f<1 else im

def run():
 ff=imageio_ffmpeg.get_ffmpeg_exe();out=P/'transformer_forward.mp4'
 cmd=[ff,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(P/'narration.wav'),'-c:v','libx264','-preset','fast','-crf','19','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-shortest',str(out)]
 with (P/'encode.log').open('w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for n in range(math.ceil(DURATION*FPS)):
   proc.stdin.write(frame(n/FPS).tobytes())
   if n%(FPS*5)==0:print('render',round(n/FPS,1),'/',round(DURATION,1),flush=True)
  proc.stdin.close();code=proc.wait()
  if code:raise RuntimeError('encode failed '+str(code))
 print('VIDEO_READY',out,flush=True)
if __name__=='__main__':
 if '--stills' in sys.argv:
  for i,z in enumerate(TIMELINE['scenes']):
   us=[u for u in TIMELINE['utterances'] if u['scene']==i]
   for j,u in enumerate(us):frame(u['start']+(u['end']-u['start'])*.7).save(P/f'preview_{i:02}_{j}.jpg',quality=94)
 else:run()
