# video-transcript-obsidian

把视频网站字幕、本地字幕文件或粘贴的 transcript 并配合[`obsidian-markdown-skill`](https://github.com/ztianyi939-wq/obsidian-markdown-skill.git) 将文稿整理成 Obsidian 友好的 Markdown 笔记。

##注意：需要这两个Skill 配合使用效果更佳。

这个 Skill 的目标不是下载视频，也不是自动破解没有字幕的视频；它负责把已经公开可取的字幕或用户提供的转录文本，转换成两类可复习资料：

1. `原始 transcript.md`：保留时间戳、来源、语言、字幕类型，便于回溯原视频。
2. `精读笔记.md`：把碎片字幕重组为中文 Obsidian 技术笔记，包含总结、时间线、概念、术语表、复习问题和相关链接。

## 适用场景

- YouTube 技术演讲、课程、讲座、访谈的视频笔记整理。
- Bilibili、会议网站、公开视频站点等可由 `yt-dlp` 读取字幕的平台。
- 已下载或手动导出的 `.srt`、`.vtt`、`.txt`、`.md` transcript 文件。
- 中英文字幕混合整理，默认输出中文精读笔记，并保留关键英文术语。
- 需要遵守 Obsidian Markdown 习惯：frontmatter、wikilinks、callouts、tags、外部来源链接。

## 能力边界

- YouTube：使用 [`youtube-transcript-api`](https://github.com/jdepoix/youtube-transcript-api) 抓取公开视频已公开的字幕轨道。
- 非 YouTube 平台：可选使用 [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) 提取网站暴露的字幕轨道。
- 本地文件：支持 `.srt`、`.vtt`、`.txt`、`.md`。
- 无字幕视频：本 Skill 不内置音频下载和语音识别流程。若平台没有公开字幕，请先提供字幕文件、粘贴 transcript，或另行使用 ASR 工具生成文本。
- 浏览器：不依赖 Chrome 或浏览器自动化抓字幕。浏览器只适合核对标题、频道、公开视频信息。

## 目录结构

```text
video-transcript-obsidian/
├─ SKILL.md
├─ README.md
├─ agents/
│  └─ openai.yaml
├─ references/
│  └─ note-structure.md
└─ scripts/
   ├─ video_transcript_to_markdown.py
   └─ fetch_youtube_transcript.py
```

## 安装为 Codex Skill

把整个目录放到 Codex skills 目录中：

```text
<CODEX_HOME>/skills/video-transcript-obsidian
```

Windows 示例：

```powershell
E:\Codex\.codex\skills\video-transcript-obsidian
```

安装后重启 Codex，或重新开启会话，让 Codex 重新发现 Skill。

推荐同时安装或保留 `$obsidian-markdown` Skill。它不是脚本运行的硬依赖，但用于生成更规范的 Obsidian 笔记，包括 frontmatter、wikilinks、callouts 和内部链接。

## Python 依赖

进入你希望运行脚本的 Python 环境后安装：

```powershell
python -m pip install youtube-transcript-api yt-dlp
```

最小依赖：

- `youtube-transcript-api`：YouTube 字幕抓取必需。
- `yt-dlp`：非 YouTube 网站字幕提取可选，但推荐安装。

## 快速开始

### 1. 列出 YouTube 字幕轨道

```powershell
python .\scripts\video_transcript_to_markdown.py "https://www.youtube.com/watch?v=VIDEO_ID" --list
```

建议优先选择人工字幕。如果只有自动字幕，也可以抓取，但精读笔记中应标明 transcript 质量风险。

### 2. 抓取 YouTube transcript

```powershell
python .\scripts\video_transcript_to_markdown.py "https://www.youtube.com/watch?v=VIDEO_ID" `
  --output "C:\path\to\vault\Video Title transcript.md" `
  --title "Video Title" `
  --speaker "Speaker Name" `
  --channel "Channel Name" `
  --languages "en,zh-Hans,zh-CN,zh"
```

脚本支持常见 YouTube 格式：

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/live/VIDEO_ID`
- 直接传入 11 位 video ID

### 3. 尝试非 YouTube 网站字幕

```powershell
python .\scripts\video_transcript_to_markdown.py "https://example.com/video-page" `
  --backend yt-dlp `
  --output "C:\path\to\vault\Video Title transcript.md" `
  --languages "en,zh-Hans,zh-CN,zh"
```

这条路径取决于 `yt-dlp` 是否支持该网站，以及该视频是否公开暴露字幕。比如部分 Bilibili 视频没有公开字幕轨道时，脚本会明确失败，而不是生成伪内容。

### 4. 转换本地字幕文件

```powershell
python .\scripts\video_transcript_to_markdown.py "C:\path\to\captions.zh-Hans.vtt" `
  --backend file `
  --output "C:\path\to\vault\Video Title transcript.md" `
  --title "Video Title"
```

支持 `.srt`、`.vtt`、`.txt`、`.md`。如果本地文本没有时间戳，脚本仍会生成可读 raw transcript，后续可以继续整理为精读笔记。

## 在 Codex 中调用

可以这样向 Codex 提需求：

```text
使用 $video-transcript-obsidian，把这个 YouTube 技术演讲整理成 Obsidian 笔记：
https://www.youtube.com/watch?v=VIDEO_ID

输出到：C:\path\to\vault
要求：保留 raw transcript，另外生成中文精读笔记，使用 wikilinks 和 callouts。
```

如果你还安装了 `$obsidian-markdown`，可以一起指定：

```text
使用 $video-transcript-obsidian 和 $obsidian-markdown，
抓取这个视频字幕，并整理成中文 Obsidian 精读笔记。
```

## 输出文件建议

推荐生成两个文件：

```text
Video Title transcript.md
Video Title 精读笔记.md
```

raw transcript frontmatter 示例：

```yaml
---
title: "Video Title transcript"
source: "https://www.youtube.com/watch?v=VIDEO_ID"
video_id: "VIDEO_ID"
channel: "Channel Name"
speaker: "Speaker Name"
language: "en"
generated: false
backend: "youtube"
created: "2026-05-25"
tags:
  - video-transcript
  - youtube
  - obsidian
---
```

精读笔记建议结构：

```markdown
# Video Title 精读笔记

## 一句话总结
## 核心脉络
## 时间线笔记
## 关键概念整理
## 术语表
## 复习问题
## 相关笔记
## 原始视频
```

更多结构建议见 `references/note-structure.md`。

## 推荐工作流

1. 识别来源：YouTube、其他视频网站、本地字幕、粘贴 transcript。
2. 先运行 `--list` 查看字幕语言和是否为自动字幕。
3. 优先抓取人工字幕；没有人工字幕时再考虑自动字幕。
4. 生成 raw transcript，保留时间戳链接和 frontmatter。
5. 读取 transcript，不逐句堆砌，而是按主题重组。
6. 生成中文 Obsidian 精读笔记，保留关键英文术语。
7. 检查 frontmatter 是否闭合、中文是否乱码、来源链接是否可追溯。

## 术语修正建议

自动字幕常会误识别专业术语。整理技术视频时，建议在生成精读笔记前先统一修正术语，例如：

- CMOS、CCD、ADC、CDS、ISP
- photodiode、pixel、column bus、ramp generator
- dark current、read noise、shot noise、dynamic range
- Bayer pattern、quantum efficiency、full well capacity

这个 Skill 是话题泛化的：不限定 CMOS 或半导体视频。面对不同主题时，应根据 transcript 自动提取领域术语，并在笔记中保留原文关键英文表达。

## 常见问题

### `ModuleNotFoundError: youtube_transcript_api`

安装依赖：

```powershell
python -m pip install youtube-transcript-api
```

### 非 YouTube 链接无法抓取字幕

先确认已安装 `yt-dlp`：

```powershell
python -m pip install yt-dlp
```

然后运行：

```powershell
python .\scripts\video_transcript_to_markdown.py "VIDEO_URL" --backend yt-dlp --list
```

如果仍然没有字幕轨道，说明该视频没有公开可提取字幕。请改用本地字幕文件或粘贴 transcript。

### YouTube 没有字幕或 transcript disabled

这通常是视频本身未开放字幕，或字幕接口不可用。Skill 不会绕过平台限制。可选方案是手动导出字幕、开启 YouTube 页面 transcript 后复制文本，或使用独立 ASR 工具生成字幕。

### 中文乱码

确保用 UTF-8 读写 Markdown 文件。PowerShell 中建议使用支持 UTF-8 的 Python 环境，并避免把输出重定向到非 UTF-8 编码文件。

## 发布到 GitHub 前建议

- 添加许可证文件，例如 `LICENSE`。
- 在 README 中替换示例路径为你的仓库实际路径。
- 不要提交个人 Obsidian vault 内容、私有视频 transcript 或含版权风险的大段字幕。
- 如要分享完整可运行版本，请提交整个 `video-transcript-obsidian/` 目录，而不只是 `SKILL.md`。

## 第三方项目

本 Skill 调用或建议安装以下开源工具：

- [`youtube-transcript-api`](https://github.com/jdepoix/youtube-transcript-api)：YouTube transcript 抓取。
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)：多平台视频元数据和字幕提取。

