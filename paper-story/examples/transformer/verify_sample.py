import os
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['OMP_NUM_THREADS']='2'
from pathlib import Path
import json,subprocess,numpy as np,soundfile as sf
import imageio_ffmpeg
from fontTools.ttLib import TTFont
import render_story as r, drawing, technical
P=Path(__file__).resolve().parent
T=json.loads((P/'timeline.json').read_text())
FONT=TTFont(P/'assets/NotoSansSC-Regular.ttf').getBestCmap()
missing=set();overflows=[];count=0
original_text=drawing.text

def checked_text(im,s,x,y,size=30,color=r.INK,bold=False,center=False,alpha=1):
 global count
 count+=1;missing.update(c for c in str(s) if ord(c) not in FONT)
 g=r.glyph(str(s),size,color,bold);left=x-g.width/2 if center else x
 if left<0 or left+g.width>r.W or y<0 or y+g.height>r.H:overflows.append(str(s))
 return original_text(im,s,x,y,size,color,bold,center,alpha)
r.text=checked_text;drawing.text=checked_text;technical.text=checked_text
for i in range(len(T['scenes'])):
 us=[u for u in T['utterances'] if u['scene']==i]
 for j,u in enumerate(us):
  frame=r.frame(u['start']+(u['end']-u['start'])*.7)
  frame.save(P/f'preview_{i:02}_{j}.jpg',quality=94)
assert not missing,repr(missing)
assert not overflows,overflows
wav,sr=sf.read(P/'narration.wav')
assert 120<T['duration']<240
assert abs(len(wav)/sr-T['duration'])<.001
assert np.abs(wav).max()<.99
assert len(T['scenes'])==13 and len(T['utterances'])==26
assert all(0<=u['start']<u['end']<=T['duration'] for u in T['utterances'])
assert all(0<=u['start']<u['end']<=T['duration'] for u in T['captions'])
assert json.loads((P/'synthesis.json').read_text())['complete']
assert all(abs(a['end']-b['start'])<1e-6 for a,b in zip(T['scenes'],T['scenes'][1:]))
ff=imageio_ffmpeg.get_ffmpeg_exe()
dec=subprocess.run([ff,'-v','error','-hwaccel','none','-threads','2','-i',str(P/'transformer_story.mp4'),'-f','null','-'],capture_output=True,text=True)
assert dec.returncode==0,dec.stderr
info=subprocess.run([ff,'-i',str(P/'transformer_story.mp4')],capture_output=True,text=True).stderr
assert 'Video: h264' in info and 'Audio: aac' in info
subprocess.run([ff,'-v','error','-y','-hwaccel','none','-threads','2','-filter_threads','2','-i',str(P/'transformer_story.mp4'),'-vf','fps=1/23,scale=480:270,tile=4x2','-frames:v','1',str(P/'encoded_contact_sheet.jpg')],capture_output=True,check=True)
report={'duration_seconds':T['duration'],'resolution':'1600x900','fps':25,'voice':'Microsoft zh-CN-XiaoxiaoNeural / edge-tts online','drawing':'Pillow, CPU','encoding':'software libx264, 2 threads','local_gpu_used':False,'cloud_device':'unknown','full_decode_ok':True,'video_track':'H264','audio_track':'AAC 24 kHz mono','audio_peak':float(np.abs(wav).max()),'timeline_and_captions_ok':True,'caption_count':len(T['captions']),'voice_request_count':len(json.loads((P/'synthesis.json').read_text())['requests']),'text_draw_calls_checked':count,'missing_glyphs':list(missing),'off_canvas_text':overflows,'toy_attention':'NumPy CPU: [0.2,0.5,0.3] @ [[1,0],[0,1],[1,1]] = [0.5,0.8]','narrative_coverage':['研究背景','核心主张','完整结构与简化前向','明确实验对比','代价与延伸问题'],'technical_segment_seconds':T['scenes'][10]['end']-T['scenes'][3]['start'],'evidence_check':'Table 2 EN-DE: 28.4 vs 26.36 BLEU; 2.3e19 vs 7.7e19 estimated FLOPs','browser_playback':'not checked by this script'}
(P/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
