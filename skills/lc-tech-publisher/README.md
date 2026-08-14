# LongCipher Tech Publisher

一个可安装的 Agent Skill:把一篇文章自动转成 LongCipher 品牌媒体包 —— **4 种比例封面图(16:9 / 9:16 / 4:3 / 3:4)× 中英双版 + 双人对话播客 MP3(中英双版) + 浅色"固定组件"口播讲解视频(中英双版)**。中文配音默认用 **Microsoft Edge Neural TTS 双人声**(男 `zh-CN-YunxiNeural` + 女 `zh-CN-XiaoxiaoNeural`);英文版统一用 `en-US-AndrewNeural`(单声线)。均免费、零 API key、无需参考录音,需联网 + `pip install edge-tts`;可选切换本地 **Fun-CosyVoice3-0.5B** 做品牌声线克隆。

## 核心策略 — 固定模板 + JSON-only 生成

**LLM 不写一行 CSS / HTML / 动画。**所有视觉风格沉淀在 **4 个手工打造的固定组件模板**(封面卡 / 金句卡 / 三点总结卡 / 结尾卡)中。LLM 在流水线里只负责输出结构化 JSON(`title` / 核心观点 / TTS 文本 / 颜色主题名)。

这样做的好处:

1. **视觉 100% 可控** — 每次输出看起来都严格遵循 LongCipher 设计系统,不会出现"AI 味"的随机样式。
2. **调试成本几乎为零** — 任何样式问题都集中在 4 个 HTML 模板里,LLM 不会"瞎改"。
3. **品牌一致** — 一个品牌设计师可以只通过改 4 个模板 + 几个 CSS 变量(`--accent`、`--ink`、`--canvas`)就重塑整个媒体包。

内容方向:两类 — `knowledge`(单主题深度分享)与 `digest`(每日多要点串讲)。详见 `references/brand-design.md` §9。

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
| **Edge TTS**(默认,`edge-tts` 依赖) | 免费双人神经语音,男 `zh-CN-YunxiNeural` + 女 `zh-CN-XiaoxiaoNeural`,无参考录音 | `uv sync` + 联网 |
| **CosyVoice3 环境**(可选) | 品牌声线 TTS 推理 | `COSYVOICE_HOME` / `COSYVOICE_MODEL` 可解析 |
| **品牌参考音色** `COSYVOICE_PROMPT_WAV` + `COSYVOICE_PROMPT_TEXT`(仅 CosyVoice 模式) | zero-shot 克隆的"品牌声线" | 同上 |

> 流水线**整体用 Python 编写**,由 `uv` 管理虚拟环境与依赖(`edge-tts` 已写入 `pyproject.toml`)。两种 TTS 后端各有一层薄 Python 封装(`scripts/edge_tts.py` / `scripts/cosyvoice_tts.py`);只有渲染环节通过 `npx hyperframes` 调用一个 Node 运行时。详见 `references/tts.md`。

## 目录结构

```text
skills/lc-tech-publisher/
├── pyproject.toml             # uv 项目(edge-tts 依赖)
├── uv.lock                    # 锁定依赖(提交)
├── SKILL.md                   # 7 步流水线调度(Agent 入口)
├── references/
│   ├── brand-design.md        # 品牌视觉规范(LongCipher tokens + 4 固定组件表 + 内容模式)
│   ├── motion-audio.md        # 动效语言 + 音频规范
│   ├── composition-contract.md# HyperFrames composition 契约
│   ├── script-schema.md       # script.json schema 详尽定义
│   └── tts.md                 # TTS 方案(Edge 默认 + CosyVoice 可选)
├── scripts/
│   ├── check_env.py           # 环境检查(ffmpeg + hyperframes + TTS 后端)
│   ├── parse_article.py       # 文章 → 大纲 + script.json schema 校验
│   ├── generate_audio.py      # 逐对话轮 TTS → 说话人时间轴 + 播客音轨(--tts edge|cosyvoice)
│   ├── edge_tts.py            # Edge Neural TTS 薄封装
│   ├── cosyvoice_tts.py       # CosyVoice3 推理薄封装
│   ├── build_cover.py         # 4 比例封面 HTML 生成(注入品牌 token + logo)
│   ├── build_composition.py   # 浅色固定组件视频组合(GSAP 时间轴对齐对话时间轴)
│   ├── render_cover.py        # 封面渲染 → PNG(支持 4 比例)
│   ├── render_video.py        # 视频渲染 + 音轨合成
│   └── verify_media.py        # ffprobe 媒体校验
├── assets/
│   ├── logos/lc.svg           # LongCipher 六边形 logo
│   └── templates/
│       ├── cover.html         # 浅色封面模板(比例自适应,data-duration=2.4s)
│       ├── dashboard.html      # 浅色视频主模板(5 种 slide 内嵌 + caption + audio clips)
│       └── shorts.html         # 浅色竖屏 9:16 短视频模板
└── README.md
```

## 工作流(Agent 自动执行)

```text
文章 → parse-article → script.json(中/英 双人对话 podcast[En] + slides[En])
     → generate-audio --lang zh / --lang en → 逐轮 WAV + speaker_timestamps[.json|_en.json] + podcast_full[_en]
     → build-cover    --lang zh / en → cover_{16x9,9x16,4x3,3x4}.html(各 4 张)
     → build-composition --lang zh / en → index.html(浅色固定组件,动画时长 = 对话时间轴)
     → lint + check(两套)
     → render → output/cover{_,_en}_*.png, podcast_full{,_en}.mp3, explainer_video_zh{,_en}.mp4
```

关键设计:

- **固定 4 套模板,LLM 只产 JSON**:视觉风格由手工模板决定(`cover` / `keypoint` / `three_points` / `outro`),LLM 写标题、金句、三点、结尾 — 不写任何 CSS。同一脚本每天都长得一样,且严格遵循 DESIGN.md(浅底、单一品牌蓝 `#0a72ef`、DM Sans + JetBrains Mono、2px ceiling、shadow-as-border)。
- **默认免费双人声 + 英文单声线**:中文用 Edge Neural TTS(男 `zh-CN-YunxiNeural` + 女 `zh-CN-XiaoxiaoNeural`);英文版统一用 `en-US-AndrewNeural`。零 API key、无参考录音,`uv sync` 安装 `edge-tts` + 联网即可。可选 `--tts cosyvoice` 切 CosyVoice3 品牌声线。
- **音画精确对齐**:说话人时间轴 `speaker_timestamps.json` 直接取 ffprobe 测得的真实音频时长;caption 在 `turns[].start/end` 处切换;slides 在 `[HERO_DURATION, total]` 区间均匀分布。
- **浅色 + 领域无关**:所有生成 HTML 严格遵循 `references/brand-design.md`(浅底 `#fafbfc`、单一品牌蓝、DM Sans + JetBrains Mono)。视觉品质与内容领域无关。
- **确定性渲染**:相同输入永远产出相同视频。

## 手动运行(不依赖 Agent 也可以)

```bash
# 1. 检查环境(默认校验 Edge 后端;--tts cosyvoice 校验 CosyVoice 后端)
uv run python scripts/check_env.py
uv run python scripts/check_env.py --tts cosyvoice

# 2. 解析文章 → 大纲
uv run python scripts/parse_article.py --input article.md --output dist/article.json
#    然后由你(或 LLM)根据大纲撰写 dist/script.json(参考 SKILL.md Step 2 schema)

# 3. 生成音频(默认 Edge TTS 双人声)—— 中文 + 英文各一遍
uv sync                                  # 首次:创建 .venv 并安装 edge-tts
uv run python scripts/generate_audio.py --script dist/script.json --lang zh --out dist
uv run python scripts/generate_audio.py --script dist/script.json --lang en --out dist   # 英文:en-US-AndrewNeural

# 4. 生成 4 比例封面 + 视频组合(中英各一套)
uv run python scripts/build_cover.py        --script dist/script.json --lang zh --out dist/cover
uv run python scripts/build_cover.py        --script dist/script.json --lang en --out dist/cover_en
uv run python scripts/build_composition.py  --script dist/script.json --lang zh --out dist/video
uv run python scripts/build_composition.py  --script dist/script.json --lang en --out dist/video_en

# 5. 渲染交付(中英各一套)
for lang in "" _en; do
  for r in 16x9 9x16 4x3 3x4; do
    uv run python scripts/render_cover.py --project "dist/cover$lang" --name "cover_$r" --output "output/cover$lang_$r.png"
  done
done
uv run python scripts/render_video.py --project dist/video     --audio dist/podcast_full.wav     --output output/explainer_video_zh.mp4
uv run python scripts/render_video.py --project dist/video_en --audio dist/podcast_full_en.wav --output output/explainer_video_en.mp4 --lang en
uv run python scripts/render_video.py --audio-only --lang zh --project dist --output output/podcast_full.mp3
uv run python scripts/render_video.py --audio-only --lang en --project dist --output output/podcast_full_en.mp3
uv run python scripts/verify_media.py output/explainer_video_zh.mp4
uv run python scripts/verify_media.py output/explainer_video_en.mp4
```