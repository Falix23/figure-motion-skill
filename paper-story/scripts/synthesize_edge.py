#!/usr/bin/env python3
"""edge-tts 单并发配音、缓存、句级边界和时间轴；本机只用 CPU。"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import argparse,asyncio,array,hashlib,html,json,shutil,subprocess,time,wave,sys
from pathlib import Path
import edge_tts

def ffmpeg_path():
 f=shutil.which('ffmpeg')
 if f:return f
 try:
  import imageio_ffmpeg
  return imageio_ffmpeg.get_ffmpeg_exe()
 except ImportError:raise RuntimeError('需要 ffmpeg CLI 或 imageio-ffmpeg 包')

def run_ffmpeg(ff,args):
 r=subprocess.run([ff,'-v','error','-threads','2',*args],capture_output=True)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace'))
 return r.stdout

def decode(ff,p):
 b=run_ffmpeg(ff,['-hwaccel','none','-i',str(p),'-f','s16le','-ar','24000','-ac','1','pipe:1'])
 if not b:raise ValueError('空音频：'+str(p))
 return b

def srt_time(t):
 n=round(t*1000);h,n=divmod(n,3600000);m,n=divmod(n,60000);sec,n=divmod(n,1000)
 return f'{h:02}:{m:02}:{sec:02},{n:03}'

async def synthesize(src,out):
 data=json.loads(src.read_text());scenes=data['scenes'];cfg=data.get('voice',{})
 if not scenes or any(not s.get('lines') for s in scenes):raise ValueError('scenes 与 lines 不能为空')
 voice=cfg.get('speaker','zh-CN-XiaoxiaoNeural');rate=cfg.get('rate','-5%');pitch=cfg.get('pitch','+0Hz')
 for s in scenes:
  if 'speech_lines' in s and len(s['speech_lines'])!=len(s['lines']):raise ValueError('speech_lines 与 lines 必须等长')
 out.mkdir(parents=True,exist_ok=True);raw=out/'raw_audio';raw.mkdir(exist_ok=True)
 ff=ffmpeg_path();sr=24000;parts=[];utterances=[];captions=[];timeline=[];requests=[];cursor=0.;last_start=None
 silence=lambda seconds:b'\0\0'*round(sr*seconds)
 def append(blob):
  nonlocal cursor
  parts.append(blob);cursor+=len(blob)/(2*sr)
 for i,scene in enumerate(scenes):
  scene_start=cursor;append(silence(.22))
  for j,display in enumerate(scene['lines']):
   speech=scene.get('speech_lines',scene['lines'])[j]
   key=hashlib.sha256(json.dumps([speech,voice,rate,pitch,'SentenceBoundary'],ensure_ascii=False).encode()).hexdigest()[:16]
   mp3=raw/f'{i:02}_{j:02}_{key}.mp3';boundary=mp3.with_suffix('.jsonl')
   cached=mp3.exists() and mp3.stat().st_size>0 and boundary.exists()
   elapsed=0.
   if not cached:
    for attempt in range(3):
     if last_start is not None:await asyncio.sleep(max(0.,4-(time.monotonic()-last_start)))
     last_start=time.monotonic();start=last_start
     temp=mp3.with_suffix('.mp3.part');meta=boundary.with_suffix('.jsonl.part')
     try:
      c=edge_tts.Communicate(speech,voice,rate=rate,pitch=pitch,boundary='SentenceBoundary')
      await asyncio.wait_for(c.save(str(temp),str(meta)),timeout=60)
      if not temp.exists() or not temp.stat().st_size:raise RuntimeError('服务返回空音频')
      temp.replace(mp3);meta.replace(boundary);elapsed=time.monotonic()-start;break
     except Exception as e:
      for tmp in [temp,meta]:
       if tmp.exists():tmp.unlink()
      status=getattr(e,'status',None)
      if status not in (429,500,502,503,504) or attempt==2:
       requests.append({'scene':i,'line':j,'error':repr(e),'voice':voice})
       (out/'synthesis.json').write_text(json.dumps({'requests':requests,'complete':False},ensure_ascii=False,indent=2))
       raise
      headers=getattr(e,'headers',None) or {};delay=8*(2**attempt)
      try:delay=max(delay,float(headers.get('Retry-After',0)))
      except (ValueError,TypeError):pass
      if delay>60:raise RuntimeError('服务要求较长等待，停止本轮；保留缓存后重运行') from e
      print('暂时受限，等待',delay,'秒',flush=True);await asyncio.sleep(delay)
   pcm=decode(ff,mp3);length=len(pcm)/(2*sr);start=cursor
   utterances.append({'text':display,'start':start,'end':start+length,'scene':i})
   local_caps=[]
   if speech==display:
    for line in boundary.read_text().splitlines():
     chunk=json.loads(line)
     if chunk.get('type')!='SentenceBoundary':continue
     a=max(0.,float(chunk['offset'])/10000000);b=min(length,a+float(chunk['duration'])/10000000)
     if b>a:local_caps.append({'text':html.unescape(chunk['text']),'start':start+a,'end':start+b,'scene':i})
   captions.extend(local_caps or [utterances[-1].copy()])
   append(pcm);append(silence(.15))
   row={'scene':i,'line':j,'voice':voice,'rate':rate,'pitch':pitch,'cache_key':key,'cached':cached,'request_seconds':round(elapsed,3),'audio_seconds':length,'audio':str(mp3.resolve()),'boundaries':str(boundary.resolve())}
   requests.append(row);print('配音',i,j,'时长',round(length,2),'缓存' if cached else '在线合成',flush=True)
   (out/'synthesis.json').write_text(json.dumps({'provider':'edge-tts / Microsoft Edge online','voice':voice,'local_gpu':False,'cloud_device':'unknown','complete':False,'requests':requests},ensure_ascii=False,indent=2))
  append(silence(.32));timeline.append({'id':scene.get('id',str(i)),'start':scene_start,'end':cursor})
 # 统一峰值而不做变速，保留声线、重音与自然停顿。
 pcm=array.array('h');pcm.frombytes(b''.join(parts))
 if sys.byteorder!='little':pcm.byteswap()
 peak=max(abs(v) for v in pcm);gain=.86*32767/max(1,peak)
 pcm=array.array('h',(round(v*gain) for v in pcm))
 if sys.byteorder!='little':pcm.byteswap()
 with wave.open(str(out/'narration.wav'),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())
 run_ffmpeg(ff,['-y','-i',str(out/'narration.wav'),'-c:a','libmp3lame','-b:a','128k',str(out/'narration.mp3')])
 result={'duration':cursor,'scenes':timeline,'utterances':utterances,'captions':captions,'voice':voice,'rate':rate,'pitch':pitch,'local_device':'cpu','voice_service':'online','server_device':'unknown'}
 (out/'timeline.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 (out/'captions.srt').write_text('\n\n'.join(f"{n+1}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}" for n,c in enumerate(captions))+'\n')
 (out/'chapters.json').write_text(json.dumps([{**z,'label':s.get('label',z['id']),'title':s.get('title','')} for z,s in zip(timeline,scenes)],ensure_ascii=False,indent=2))
 (out/'synthesis.json').write_text(json.dumps({'provider':'edge-tts / Microsoft Edge online','voice':voice,'local_gpu':False,'cloud_device':'unknown','complete':True,'duration':cursor,'requests':requests,'free_service_notice':'本次无需API Key调用成功，不承诺永久免费、无配额或随时可用'},ensure_ascii=False,indent=2))
 print('AUDIO_READY',round(cursor,3),voice,'captions',len(captions),flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('storyboard',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 asyncio.run(synthesize(a.storyboard.resolve(),a.output.resolve()))
if __name__=='__main__':main()
