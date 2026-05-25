# Video Transcript Obsidian Skill

Extract video transcripts and turn them into Obsidian-ready Markdown notes.

This skill helps Codex or another compatible agent fetch or ingest subtitles from YouTube, supported video sites, or local transcript files, then produce readable notes that work well inside an Obsidian vault.

## What it helps with

- Fetch YouTube transcripts with `youtube-transcript-api`.
- Try subtitle extraction from other video sites with `yt-dlp`.
- Convert local `.srt`, `.vtt`, `.txt`, or `.md` transcripts into Markdown.
- Save raw timestamped transcript notes for traceability.
- Create cleaned Obsidian notes with summaries, timelines, concepts, terms, review questions, wikilinks, and callouts.
- Handle Chinese and English captions; default cleaned notes can be written in Chinese while preserving key English terms.

## Install

Install with the Codex skill installer:

```powershell
python E:\Codex\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --url https://github.com/YOUR_NAME/video-transcript-obsidian --path . --name video-transcript-obsidian --dest E:\Codex\.codex\skills
```

Or manually download this repository and place it at:

```text
E:\Codex\.codex\skills\video-transcript-obsidian
```

The final structure should contain:

```text
E:\Codex\.codex\skills\video-transcript-obsidian\SKILL.md
```

Restart Codex after installing.

## Dependencies

Install Python dependencies in the environment where you run the scripts:

```powershell
python -m pip install youtube-transcript-api yt-dlp
```

`youtube-transcript-api` is required for YouTube. `yt-dlp` is optional, but recommended for non-YouTube subtitle extraction.

## Usage

Example prompts:

```text
Use $video-transcript-obsidian to turn this YouTube technical talk into an Obsidian note:
https://www.youtube.com/watch?v=VIDEO_ID
```

```text
Use $video-transcript-obsidian and $obsidian-markdown to create a Chinese Obsidian study note from this video. Save both the raw transcript and the cleaned note.
```

```text
Use $video-transcript-obsidian to convert this local .vtt subtitle file into a timestamped Markdown transcript, then summarize it as an Obsidian note.
```

## Script examples

List available YouTube transcript tracks:

```powershell
python .\scripts\video_transcript_to_markdown.py "https://www.youtube.com/watch?v=VIDEO_ID" --list
```

Fetch a YouTube transcript:

```powershell
python .\scripts\video_transcript_to_markdown.py "https://www.youtube.com/watch?v=VIDEO_ID" --output "Video Title transcript.md" --languages "en,zh-Hans,zh-CN,zh"
```

Try a non-YouTube video site with `yt-dlp`:

```powershell
python .\scripts\video_transcript_to_markdown.py "https://example.com/video-page" --backend yt-dlp --list
```

Convert a local subtitle file:

```powershell
python .\scripts\video_transcript_to_markdown.py "captions.vtt" --backend file --output "Video Title transcript.md"
```

## Notes

This skill only uses transcripts or subtitles that are available to you. It does not bypass platform restrictions and does not include audio transcription. If a video has no accessible subtitles, provide a local subtitle file or pasted transcript.

For best Obsidian formatting, use this skill together with [`obsidian-markdown`](https://github.com/ztianyi939-wq/obsidian-markdown-skill.git).

## Attribution

This skill uses or supports these open-source tools:

- [`youtube-transcript-api`](https://github.com/jdepoix/youtube-transcript-api)
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)

