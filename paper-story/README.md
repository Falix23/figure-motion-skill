# 论文故事动画 · paper-story

阅读论文全文、图表与相关附录，将背景、主张、方法结构、一次关键过程、实验证据和局限组织为带配音、字幕的动画讲解。目标是让观众建立理解并形成问题。

[Skill说明](SKILL.md) · [配音输入](references/production.md) · [产物交付规范](references/delivery.md)

## 安装

需要Python 3.10+。本机配音编排、绘图和软件编码均可使用CPU；不需要下载语音大模型或配置GPU。

```bash
cd paper-story
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

安装为Codex技能时，将本目录的SKILL.md、agents、scripts、references及examples完整复制到 `~/.codex/skills/paper-story/`。技能默认可被自动发现；也可显式调用 `$paper-story`。

## 先离线查看画面

不调用语音接口、不生成音频和视频，只检查分镜和字体。时间轴为估算，页面会明确标记。

```bash
python scripts/build_transformer_example.py --preview-only --output outputs/transformer-preview
python -m http.server 8000 --bind 127.0.0.1
```

打开 `http://127.0.0.1:8000/outputs/transformer-preview/index.html`。

## 生成完整Transformer示例

此命令会把示例口播发送到微软在线语音服务。它使用edge-tts社区客户端调用晓晓，当前无需API Key，但没有永久免费、无限额或服务持续可用的保证。在线服务后台设备未知；本机不使用GPU。

```bash
CUDA_VISIBLE_DEVICES="" python scripts/build_transformer_example.py --output outputs/transformer-video --host "我的电脑"
```

生成MP4、独立MP3/WAV、句级SRT、口播和分镜、时间轴、原始分段配音与边界、截图、源码副本和完整产物清单。输出目录非空时显式传 `--resume` 续做；成功配音按内容与音色缓存，不重复请求。请求单并发，限制频率，短暂限流只做有限重试，不轮换账号或端点绕过配额。

也可以使用口播完全相同的既有配音工程，无需访问在线服务：

```bash
python scripts/build_transformer_example.py --audio-project /path/to/existing-project --output outputs/reused-audio --host "运行机器"
```

## 完整代码结构

- `scripts/synthesize_edge.py`：分镜的在线配音、缓存、句级边界与实际时间轴。
- `scripts/inventory_artifacts.py`：逐文件角色、机器、绝对路径、大小、SHA256与交付Markdown。
- `scripts/build_transformer_example.py`：独立构建示例、生成播放页、验证与清单。
- `examples/transformer/`：完整文案、分镜、依据、CPU绘图与编码源码、数值算例、字体及OFL许可。

示例包括编码器—解码器各六层、位置编码、自注意力、多头、前馈、原始Post-LN、因果掩码、交叉注意力与自回归生成，并交代研究背景、明确实验对比与长序列开销。权重、维度与预测概率为教学简化，不是预训练模型实测。

这是Agent工作流加一套完整示例，不是任意PDF的一键自动视频模型。其他论文需要Agent阅读资料，并编写符合其方法的分镜和动画；当前Transformer渲染器不套用于其他论文。

## 交付必须告知文件

每次生成后，回复必须说明保存机器、完整输出目录、视频/音频/字幕/文案/工程等真实产物及下载入口。artifacts.json、artifacts.md不能替代回复中的说明。远程开发机不等于用户本机；同时说明保留的模型、依赖和旧版缓存，不自动删除。

## 验证与许可

完整生成会执行数值算例、字形与画布边界检查、字幕/音轨时长检查和视频全片解码。浏览器播放、人工听辨与这些自动检查分别报告。

源码沿用仓库MIT许可；Noto Sans SC示例字体采用SIL OFL 1.1，见 examples/transformer/assets/OFL.txt。字体为当前示例子集，添加文字后须重新检查字形覆盖。

生成的音视频、模型、环境和缓存不随源码提交。不要将私人论文、密钥或业务资料提交到仓库。
