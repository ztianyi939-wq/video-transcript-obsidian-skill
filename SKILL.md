---
name: video-transcript-obsidian
description: Extract or ingest video transcripts from YouTube, many yt-dlp-supported video sites, local subtitle files (.srt/.vtt), plain transcript text, or pasted transcripts, then turn them into readable Obsidian Markdown notes. Use for technical talks, lectures, conference videos, bilingual Chinese/English captions, topic-agnostic video notes, raw timestamped transcript Markdown, cleaned Chinese Obsidian summaries, frontmatter, wikilinks, callouts, terminology cleanup, timelines, and review questions.
---

# Video Transcript Obsidian

Convert a video transcript into two Obsidian-friendly artifacts:

1. A raw timestamped transcript Markdown file for traceability.
2. A cleaned technical note with summaries, timeline links, concepts, terms, and review questions.

Use `$obsidian-markdown` as the companion skill when available. Follow its conventions for YAML frontmatter, wikilinks, callouts, tags, and external links.

## Capability Boundaries

- **YouTube**: Use `youtube-transcript-api` for reliable transcript listing/fetching without browser automation.
- **Other video sites**: Use optional `yt-dlp` subtitle extraction when the site and video expose captions/subtitles. This supports many platforms, but cannot invent subtitles when none exist.
- **Local or user-provided transcript**: Ingest `.srt`, `.vtt`, `.txt`, or `.md` files and convert them into timestamped Markdown.
- **Languages**: Prefer user-requested languages. Default preference is English plus Simplified/Chinese variants: `en,zh-Hans,zh-CN,zh`. Preserve source language in raw transcript; summarize in Chinese unless the user asks otherwise.
- **Topics**: Topic-agnostic. Use the transcript to infer domain tags and terminology. For technical talks, correct ASR terms before summarizing.

## Workflow

1. Identify the source:
   - YouTube URL or 11-character video ID: use `scripts/video_transcript_to_markdown.py` with backend `youtube` or `auto`.
   - Other video URL: use backend `yt-dlp` or `auto`; install `yt-dlp` if missing.
   - Local subtitle/transcript file: use backend `file` or `auto`.
2. Fetch or ingest the transcript:
   - If `youtube-transcript-api` is missing, install it in the active project/local virtual environment with `python -m pip install youtube-transcript-api`.
   - If using non-YouTube URLs and `yt-dlp` is missing, install it with `python -m pip install yt-dlp`.
   - Run `--list` when language choice matters.
   - Prefer manual captions over auto-generated captions when both are available.
3. Save the raw transcript:
   - Use a filename like `<video title> transcript.md`.
   - Keep timestamp links back to the source when the source supports timestamp URLs.
   - Include source URL/path, backend, speaker/channel when known, language, and generated/manual status in frontmatter.
4. Synthesize the cleaned note:
   - Read enough transcript to infer the talk structure; aggregate tiny caption fragments into topical sections.
   - Correct obvious ASR mistakes in domain terms before summarizing.
   - Produce Chinese notes unless the user requests another language.
   - Link to the raw transcript note and related vault notes with wikilinks.
5. Validate:
   - Confirm frontmatter opens/closes with `---`.
   - Confirm source links and timestamp links are present when available.
   - Check for mojibake/replacement characters.
   - Confirm the cleaned note is readable and not just a transcript dump.

## Generic Transcript Script

From this skill directory, list tracks for YouTube:

```powershell
python .\scripts\video_transcript_to_markdown.py "https://www.youtube.com/watch?v=VIDEO_ID" --list
```

Fetch YouTube captions, preferring English then Chinese:

```powershell
python .\scripts\video_transcript_to_markdown.py "https://www.youtube.com/watch?v=VIDEO_ID" `
  --output "C:\path\to\vault\Video Title transcript.md" `
  --title "Video Title" `
  --speaker "Speaker Name" `
  --channel "Channel Name" `
  --languages "en,zh-Hans,zh-CN,zh"
```

Try a non-YouTube video site with `yt-dlp`:

```powershell
python .\scripts\video_transcript_to_markdown.py "https://example.com/video-page" `
  --backend yt-dlp `
  --output "C:\path\to\vault\Video Title transcript.md" `
  --languages "en,zh-Hans,zh-CN,zh"
```

Convert a local subtitle file:

```powershell
python .\scripts\video_transcript_to_markdown.py "C:\path\to\captions.zh-Hans.vtt" `
  --backend file `
  --output "C:\path\to\vault\Video Title transcript.md" `
  --title "Video Title"
```

The script accepts YouTube `watch?v=`, `youtu.be/`, `shorts/`, `embed/`, `live/`, raw video IDs, many `yt-dlp` supported URLs, and local `.srt`, `.vtt`, `.txt`, or `.md` files.

## Cleaned Note Structure

Read `references/note-structure.md` before writing the cleaned note. Use it for the default section layout, language handling, and terminology cleanup checklist.

Minimum cleaned note sections:

- `# <title> 精读笔记`
- `## 一句话总结`
- `## 核心脉络`
- `## 时间线笔记`
- `## 关键概念整理`
- `## 术语表`
- `## 复习问题`
- `## 相关笔记`
- `## 原始视频`

Use callouts for source/quality caveats and major takeaways. Use Markdown links for external video URLs and wikilinks for notes inside the vault.

## Failure Handling

- If transcripts are disabled or unavailable, say so and ask for a user-provided transcript or subtitle file.
- If YouTube blocks retrieval, do not try browser workarounds automatically; ask for a pasted transcript or local subtitle file.
- If `yt-dlp` cannot find subtitles for a non-YouTube site, report that the site/video did not expose captions and ask for subtitle/audio/transcript input.
- If the transcript is auto-generated, mark it clearly and correct terminology during synthesis.
- If a local transcript has no timestamps, still create a readable raw note with untimed sections, then synthesize the cleaned note.
