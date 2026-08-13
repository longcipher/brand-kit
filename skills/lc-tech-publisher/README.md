# LongCipher Tech Publisher

一个可安装的 Agent Skill:把一篇文章自动转成 LongCipher 品牌媒体包 —— **16:9 封面图 + 播客 MP3 + 口播讲解视频**。配音默认用 **Microsoft Edge Neural TTS**(`zh-CN-yunxi`,免费、零 API key、无需参考录音,需联网 + `pip install edge-tts`);可选切换本地 **Fun-CosyVoice3-0.5B** 做品牌声线克隆。

## 安装

推送到 GitHub 后(仓库 `longcipher/brand-kit`):

```bash
npx skills add longcipher/brand-kit --skill lc-tech-publisher --full-depth
```

然后在支持 Agent Skills 的 IDE / CLI(Claude Code、Cursor、Codex 等)中:

> 用 lc-tech-publisher 把 `docs/xxx.md` 这篇文章转成我们的品牌媒体包(封面 + 播客 + 视频)

## 前置条件

| 依赖 | 用途 | 检查 |
|------|------|------|
| Python >= 3.10 + `uv` | 管理 Python 项目 + 运行全部编排脚本 | `uv run python scripts/check_env.py` |
| Node.js >= 22 | 仅供 `npx --yes hyperframes` CLI 使用 | `npx --yes hyperframes --version` |
| FFmpeg / ffprobe | 音频拼接、抽帧、媒体校验 | 同上 |
| `npx --yes hyperframes` CLI | 视频渲染(build/compose/lint/check/render) | 同上 |
| **Edge TTS**(默认,`edge-tts` 依赖)**默认** | 免费神经语音,`zh-CN-yunxi`,无参考录音 | `uv sync` + 联网 |
| **CosyVoice3 环境**(可选,Python + torch + CosyVoice 仓库 + `Fun-CosyVoice3-0.5B` 模型) | 品牌声线 TTS 推理 | `COSYVOICE_HOME` / `COSYVOICE_MODEL` 可解析 |
| **品牌参考音色** `COSYVOICE_PROMPT_WAV` + `COSYVOICE_PROMPT_TEXT`(仅 CosyVoice 模式需要) | zero-shot 克隆的"品牌声线" | 同上 |

> 流水线**整体用 Python 编写**,由 `uv` 管理虚拟环境与依赖(`edge-tts` 已写入 `pyproject.toml`)。两种 TTS 后端各有一层薄 Python 封装(`scripts/edge_tts.py` / `scripts/cosyvoice_tts.py`);只有渲染环节通过 `npx hyperframes` 调用一个 Node 运行时。详见 `references/tts.md`。

## 目录结构

```text
skills/lc-tech-publisher/
├── pyproject.toml           # uv 项目(edge-tts 依赖)
├── uv.lock                  # 锁定依赖(提交)
├── SKILL.md                 # 7 步流水线调度(Agent 入口)
├── references/
│   ├── brand-design.md      # 品牌视觉规范(LongCipher tokens)
│   ├── motion-audio.md      # 动效语言 + 音频规范
│   ├── composition-contract.md  # HyperFrames composition 契约
│   └── tts.md               # TTS 方案(Edge 默认 + CosyVoice 可选)
├── scripts/
│   ├── check_env.py        # 环境检查(ffmpeg + hyperframes + TTS 后端)
│   ├── parse_article.py    # 文章 → 大纲 + script.json schema 校验
│   ├── generate_audio.py   # 逐场景 TTS → 时间戳 + 播客音轨(--tts edge|cosyvoice)
│   ├── edge_tts.py          # Edge Neural TTS 薄封装(默认后端,无需参考录音)
│   ├── cosyvoice_tts.py     # CosyVoice3 推理薄封装(可选品牌声线)
│   ├── build_cover.py      # 封面 HTML 生成(注入品牌 token + logo)
│   ├── build_composition.py# 视频组合生成(GSAP 时间轴对齐音频)
│   ├── render_cover.py     # 封面渲染 → PNG
│   ├── render_video.py     # 视频渲染 + 音轨合成
│   └── verify_media.py     # ffprobe 媒体校验
├── assets/
│   ├── logos/lc.svg         # LongCipher 六边形 logo
│   └── templates/cover.html # 品牌封面模板
└── README.md
```

## 工作流(Agent 自动执行)

```text
文章 → parse-article → script.json(场景+口播稿)
     → generate-audio → Edge/CosyVoice 逐场景 WAV + timestamps.json + podcast_full
     → build-cover    → cover.html
     → build-composition → index.html(动画时长 = 音频时长)
     → lint + check
     → render → output/cover.png, podcast_full.mp3, explainer_video.mp4
```

关键设计:

- **默认免费语音**:Edge Neural TTS(`zh-CN-yunxi`),零 API key、无需参考录音,`uv sync` 安装 `edge-tts` + 联网即可。可选 `--tts cosyvoice` 切换本地 CosyVoice3 做品牌声线克隆(需一段参考录音 `COSYVOICE_PROMPT_WAV`,本地、无 API key)。两种后端都是薄 Python 封装承载推理。
- **音画精确对齐**:场景 `data-duration` 直接取 ffprobe 测得的真实音频时长,GSAP 时间轴为绝对时间轴。
- **品牌保真**:所有生成 HTML 严格遵循 `references/brand-design.md`(`#171717`/`#ffffff`、Geist Mono 眉标、mesh gradient、6px 圆角)。
- **确定性渲染**:相同输入永远产出相同视频。

## 手动运行(不依赖 Agent 也可以)

```bash
# 1. 检查环境(默认校验 Edge 后端;--tts cosyvoice 校验 CosyVoice 后端)
uv run python scripts/check_env.py
uv run python scripts/check_env.py --tts cosyvoice

# 2. 解析文章 → 大纲
uv run python scripts/parse_article.py --input article.md --output dist/article.json
#    然后由你(或 LLM)根据大纲撰写 dist/script.json(参考 SKILL.md Step 2 schema)

# 3. 生成音频(默认 Edge TTS,无需参考录音)
uv sync                       # 首次:创建 .venv 并安装 edge-tts
uv run python scripts/generate_audio.py --script dist/script.json --out dist

#    或:本地 CosyVoice3 品牌声线
export COSYVOICE_PROMPT_WAV=/path/to/your-brand-voice.wav
export COSYVOICE_PROMPT_TEXT="参考录音的转写文本"
uv run python scripts/generate_audio.py --script dist/script.json --tts cosyvoice --speed 1.0 --lang zh --out dist

# 4. 生成封面 + 视频组合
uv run python scripts/build_cover.py --script dist/script.json --out dist/cover
uv run python scripts/build_composition.py --script dist/script.json --timings dist/timestamps.json --out dist/video

# 5. 渲染交付
uv run python scripts/render_cover.py --project dist/cover --output output/cover.png
uv run python scripts/render_video.py --project dist/video --audio dist/podcast_full.wav --output output/explainer_video.mp4
uv run python scripts/render_video.py --audio-only --project dist --output output/podcast_full.mp3
uv run python scripts/verify_media.py output/explainer_video.mp4
```
