# 配音输入与制作约定

输入 `storyboard.json`，用 scenes 描述镜头，用 lines 保存实际口播。lines 与可选 speech_lines 等长；speech_lines 仅用于发音表达调整，字幕仍用 lines。每段不应过长；合理分句而不是逐字单独合成。

```json
{"title":"论文讲解","voice":{"speaker":"zh-CN-XiaoxiaoNeural","rate":"-5%","pitch":"+0Hz"},"scenes":[{"id":"background","label":"研究背景","title":"作者面对什么问题","source":"§1","lines":["第一句口播。","第二句口播。"]}]}
```

CPU 机器安装 `edge-tts` 与可用 FFmpeg；没有 FFmpeg CLI 时脚本可使用 `imageio-ffmpeg` 提供的可执行文件。脚本的音频拼接使用标准库，不需要下载语音模型。

```sh
CUDA_VISIBLE_DEVICES="" python3 scripts/synthesize_edge.py /work/storyboard.json --output /work/video
```

脚本默认单并发，相邻请求起始间隔至少4秒。对429和临时服务端错误最多重试2次，尊重 Retry-After；超过60秒的等待提示重运行，其他错误直接停止。成功的分段按正文、音色和韵律参数缓存，重运行可续做，不能靠轮换账号或端点绕过配额。

产出 raw_audio/ 下的MP3与JSONL边界记录、合并WAV/MP3、captions.srt、timeline.json、chapters.json 和 synthesis.json。timeline 的 utterances 用于镜头语义阶段，captions 优先使用服务实际句级边界。渲染器读取更新后的时间轴并重绘，不能只替换音轨。

全文、论点来源与动画代码由当次讲解任务编写；本脚本只处理配音与时间数据，不声称自动读懂任意论文或自动输出视频。

## Transformer 可复现示例

完整源码位于 `examples/transformer/`，包含分镜、口播、来源、数值算例、CPU绘图与验证。用 `python scripts/build_transformer_example.py --preview-only --output outputs/preview` 只生成离线检查画面；去掉 `--preview-only` 时会调用已获允许的在线配音并生成完整视频。它是论文专用示例；换论文时按其结构编写动画，不直接套用Transformer过程。安装、续做与已有配音复用见 [README.md](../README.md)。
