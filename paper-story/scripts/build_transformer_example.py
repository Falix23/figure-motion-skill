#!/usr/bin/env python3
"""从可移植源码构建Transformer示例；本机计算固定CPU。"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['OMP_NUM_THREADS']='2'
os.environ['MKL_NUM_THREADS']='2'
import argparse,html,json,platform,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXAMPLE=ROOT/'examples/transformer'

def run(script,*args,cwd=None):
 subprocess.run([sys.executable,str(script),*map(str,args)],cwd=cwd,check=True)

def preview_timeline(book,out):
 cursor=0.;scenes=[];utter=[]
 for i,s in enumerate(book['scenes']):
  begin=cursor;cursor+=.22
  for line in s['lines']:
   seconds=max(1.5,len(line)/5)
   utter.append({'text':line,'start':cursor,'end':cursor+seconds,'scene':i});cursor+=seconds+.15
  cursor+=.32;scenes.append({'id':s['id'],'start':begin,'end':cursor})
 data={'duration':cursor,'scenes':scenes,'utterances':utter,'captions':utter,'estimated':True,'voice_service':'not called','local_device':'cpu'}
 (out/'timeline.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 (out/'chapters.json').write_text(json.dumps([{**z,'label':s['label'],'title':s['title']} for z,s in zip(scenes,book['scenes'])],ensure_ascii=False,indent=2))

def prepare(out,resume):
 if out.exists() and any(out.iterdir()):
  if not resume:raise ValueError('输出目录非空：使用新目录；续做本工程时传 --resume')
  if not all((out/f).is_file() for f in ['storyboard.json','render_story.py','drawing.py','technical.py']):raise ValueError('不是可续做的Transformer工程目录')
  return
 out.mkdir(parents=True,exist_ok=True)
 for f in EXAMPLE.iterdir():
  if f.is_dir():shutil.copytree(f,out/f.name,dirs_exist_ok=True)
  else:shutil.copy2(f,out/f.name)
 snapshot=out/'skill_snapshot';snapshot.mkdir(exist_ok=True)
 for name in ['SKILL.md','agents','references','scripts']:
  f=ROOT/name
  if f.is_dir():shutil.copytree(f,snapshot/name,ignore=shutil.ignore_patterns('__pycache__'))
  else:shutil.copy2(f,snapshot/name)
 (out/'make_voice.py').write_text("from pathlib import Path\nimport subprocess,sys\np=Path(__file__).resolve().parent\nsubprocess.run([sys.executable,str(p/'skill_snapshot/scripts/synthesize_edge.py'),str(p/'storyboard.json'),'--output',str(p)],check=True)\n")
 (out/'run_cpu.sh').write_text("""#!/usr/bin/env bash
set -euo pipefail
export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2
cd "$(dirname "$0")"
PYTHON="${PAPER_STORY_PYTHON:-python3}"
"$PYTHON" make_voice.py
"$PYTHON" render_story.py --stills
"$PYTHON" render_story.py
"$PYTHON" verify_sample.py
"$PYTHON" skill_snapshot/scripts/inventory_artifacts.py . --host "${PAPER_STORY_HOST:-运行机器}"
""");(out/'run_cpu.sh').chmod(0o755)

def reuse_audio(source,out):
 original=json.loads((source/'storyboard.json').read_text());book=json.loads((out/'storyboard.json').read_text())
 if [(s['id'],s['lines']) for s in original['scenes']]!=[(s['id'],s['lines']) for s in book['scenes']]:raise ValueError('已有配音与示例口播不一致，不能复用')
 for name in ['narration.wav','timeline.json','captions.srt','chapters.json','synthesis.json']:
  if not (source/name).is_file():raise ValueError('配音工程缺文件：'+name)
  shutil.copy2(source/name,out/name)
 if (source/'narration.mp3').is_file():shutil.copy2(source/'narration.mp3',out/'narration.mp3')
 if (source/'raw_audio').is_dir():shutil.copytree(source/'raw_audio',out/'raw_audio',dirs_exist_ok=True)
 book['voice']=original['voice'];(out/'storyboard.json').write_text(json.dumps(book,ensure_ascii=False,indent=2))

def player(out,preview):
 book=json.loads((out/'storyboard.json').read_text())
 if preview:
  media='<p>离线预览：未调用语音服务，未生成配音或MP4；以下时间仅为估算。</p>'+''.join('<figure><img loading="lazy" src="preview_%02d_0.jpg"><figcaption>%s</figcaption></figure>'%(i,html.escape(s['title'])) for i,s in enumerate(book['scenes']))
 else:media='<video controls preload="metadata" playsinline poster="preview_00_0.jpg"><source src="transformer_story.mp4" type="video/mp4"></video>'
 links=[('artifacts.md','产物清单'),('storyboard.json','分镜'),('timeline.json','时间轴'),('sources.md','原文依据'),('skill_snapshot/SKILL.md','Skill说明')]
 if not preview:links=[('transformer_story.mp4','视频MP4'),('narration.mp3','配音MP3'),('narration.wav','配音WAV'),('captions.srt','字幕SRT')]+links
 markup=''.join(f'<a href="{html.escape(f)}">{html.escape(title)}</a>' for f,title in links if (out/f).exists() or f=='artifacts.md')
 page="""<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Transformer论文故事</title><style>body{background:#f3f0e8;color:#262b29;font-family:system-ui;max-width:1200px;margin:32px auto;padding:0 24px}video,img{width:100%;border-radius:14px}figure{margin:25px 0}a{display:inline-block;margin:10px 20px 10px 0;color:#384d43}p{line-height:1.8}</style><h1>Transformer：从背景到方法与证据</h1>"""
 (out/'index.html').write_text(page+media+'<nav>'+markup+'</nav><p>本机绘图和编码使用CPU。在线语音（如有）由微软服务生成，后台设备未知。edge-tts不承诺永久免费、无额度或持续可用。生成文件的位置、用途与大小见产物清单。</p></html>')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'outputs/transformer');parser.add_argument('--resume',action='store_true');parser.add_argument('--host',default=platform.node()+'（运行机器）');parser.add_argument('--base-url')
 group=parser.add_mutually_exclusive_group();group.add_argument('--preview-only',action='store_true');group.add_argument('--audio-project',type=Path)
 a=parser.parse_args();out=a.output.resolve();prepare(out,a.resume);book=json.loads((out/'storyboard.json').read_text())
 if a.preview_only:preview_timeline(book,out)
 elif a.audio_project:reuse_audio(a.audio_project.resolve(),out)
 else:run(ROOT/'scripts/synthesize_edge.py',out/'storyboard.json','--output',out)
 run(out/'toy_attention.py',cwd=out);run(out/'render_story.py','--stills',cwd=out)
 if not a.preview_only:run(out/'render_story.py',cwd=out);run(out/'verify_sample.py',cwd=out)
 player(out,a.preview_only)
 report={'example':'transformer','preview_only':a.preview_only,'output_directory':str(out),'local_gpu_used':False,'voice_service':'not called' if a.preview_only else ('existing audio reused' if a.audio_project else 'edge-tts online')}
 (out/'build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 args=[out,'--host',a.host]
 if a.base_url:args+=['--base-url',a.base_url]
 run(ROOT/'scripts/inventory_artifacts.py',*args);print('BUILD_READY',out,flush=True)
if __name__=='__main__':main()
