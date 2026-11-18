#!/usr/bin/env python3
"""列出真实产物及保留缓存；不跟随符号链接，不读取凭据。"""
import argparse,datetime,hashlib,json
from pathlib import Path
from urllib.parse import quote

def role(p):
 name=p.name;parts=p.parts
 if 'skill_snapshot' in parts:return '技能说明与可复用脚本副本'
 if 'raw_audio' in parts:return '分段配音边界元数据' if p.suffix=='.jsonl' else '分段原始在线配音'
 if 'assets' in parts:return '画面字体与资源'
 exact={'index.html':'播放与下载页面','narration.wav':'独立配音（无损WAV）','narration.mp3':'独立配音（MP3）','captions.srt':'句级字幕','narration.txt':'口播稿','storyboard.json':'可编辑分镜','timeline.json':'实际音频与镜头时间轴','chapters.json':'章节索引','sources.md':'论文依据与教学简化','verification.json':'成片检查报告','synthesis.json':'配音来源与请求缓存记录','retained-assets.json':'沿用或此前保留的外部产物说明','CPU_ONLY':'本机计算设备与在线服务说明','COMPUTE_INFO.txt':'本机计算设备与在线服务说明'}
 if name in exact:return exact[name]
 if p.suffix=='.mp4':return '成片视频'
 if name.startswith('preview_') or name=='encoded_contact_sheet.jpg':return '画面检查截图'
 if p.suffix in ['.py','.sh']:return '可复现制作源码'
 if p.suffix=='.log':return '制作过程日志'
 if name.startswith('toy_attention'):return '教学注意力算例'
 return '辅助说明或数据'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);parser.add_argument('--host',required=True);parser.add_argument('--base-url');parser.add_argument('--retained',type=Path);a=parser.parse_args()
 root=a.output.resolve();files=[];links=[]
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if '__pycache__' in rel.parts or (len(rel.parts)==1 and p.name in ['artifacts.json','artifacts.md']):continue
  if p.is_symlink():links.append({'path':str(p),'target':str(p.resolve())});continue
  if not p.is_file():continue
  if p.name=='.env' or p.suffix.lower() in ['.key','.pem'] or any(t in p.name.lower() for t in ['credential','secret']):continue
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  row={'role':role(rel),'host':a.host,'path':str(p),'relative_path':str(rel),'bytes':p.stat().st_size,'sha256':h.hexdigest()}
  if a.base_url:row['url']=a.base_url.rstrip('/')+'/'+quote(str(rel))
  files.append(row)
 retained=json.loads(a.retained.read_text()) if a.retained else []
 for r in retained:
  if not Path(r['path']).exists():raise ValueError('保留条目路径不存在：'+r['path'])
 data={'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':a.host,'output_directory':str(root),'file_count':len(files),'total_bytes':sum(f['bytes'] for f in files),'files':files,'retained_assets':retained,'symlinks_not_followed':links,'inventory_note':'清单自身不递归计入摘要；不包含__pycache__和凭据文件'}
 (root/'artifacts.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 lines=['# 本次视频生成产物清单','',f'保存环境：{a.host}',f'输出目录：`{root}`',f'文件：{len(files)} 个；合计 {data["total_bytes"]:,} 字节。','', '| 产物用途 | 完整路径 | 字节数 | 下载 |','|---|---|---:|---|']
 for f in files:
  link='[下载]('+f['url']+')' if 'url' in f else '—'
  lines.append(f"| {f['role']} | `{f['path']}` | {f['bytes']:,} | {link} |")
 lines+=['','## 沿用或此前仍保留的外部产物','']
 for r in retained:lines.append(f"- {r['role']}：`{r['path']}`（{r['host']}；{r.get('status','')}）。{r.get('purpose','')}"+(' 大小：'+str(r['bytes'])+' 字节。' if 'bytes' in r else ''))
 lines+=['','清单文件自身为 artifacts.json 与 artifacts.md。跨机器副本须另行据实说明。']
 (root/'artifacts.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'host':a.host,'directory':str(root),'files':len(files),'bytes':data['total_bytes']},ensure_ascii=False))
if __name__=='__main__':main()
