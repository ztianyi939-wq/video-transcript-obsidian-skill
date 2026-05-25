from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse


class TranscriptError(RuntimeError):
    pass


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_youtube(value: str) -> bool:
    parsed = urlparse(value)
    host = parsed.netloc.lower()
    return host.endswith("youtube.com") or host.endswith("youtube-nocookie.com") or host.endswith("youtu.be")


def parse_youtube_id(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")

    if host.endswith("youtu.be"):
        candidate = path.split("/")[0]
    elif host.endswith("youtube.com") or host.endswith("youtube-nocookie.com"):
        if path == "watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        elif path.startswith(("shorts/", "embed/", "live/")):
            candidate = path.split("/")[1]
        else:
            candidate = ""
    else:
        candidate = ""

    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
        raise TranscriptError(f"Could not parse a YouTube video id from: {value}")
    return candidate


def format_stamp(seconds: float | None) -> str:
    if seconds is None:
        return "no-time"
    whole = max(0, int(seconds))
    hours = whole // 3600
    minutes = (whole % 3600) // 60
    secs = whole % 60
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def parse_stamp(value: str) -> float:
    value = value.strip().replace(",", ".")
    match = re.fullmatch(r"(?:(\d+):)?(\d{1,2}):(\d{1,2})(?:\.(\d{1,3}))?", value)
    if not match:
        raise ValueError(value)
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    millis = int((match.group(4) or "0").ljust(3, "0"))
    return hours * 3600 + minutes * 60 + seconds + millis / 1000


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(html.unescape(text).split())


def slug_title(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", value)
    value = " ".join(value.split())
    return value[:120] or "video transcript"


def timestamp_link(source: str, seconds: float | None) -> str:
    if seconds is None or not is_url(source):
        return ""
    parsed = urlparse(source)
    if is_youtube(source):
        video_id = parse_youtube_id(source)
        return f"https://www.youtube.com/watch?v={video_id}&t={int(seconds)}s"
    sep = "&" if parsed.query else "?"
    return f"{source}{sep}t={int(seconds)}"


def import_youtube_transcript_api():
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            CouldNotRetrieveTranscript,
            NoTranscriptFound,
            TranscriptsDisabled,
            VideoUnavailable,
        )
    except ImportError as exc:
        raise TranscriptError(
            "Missing dependency for YouTube: install with `python -m pip install youtube-transcript-api`."
        ) from exc
    return (
        YouTubeTranscriptApi,
        CouldNotRetrieveTranscript,
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    )


def list_youtube(source: str) -> list[dict]:
    YouTubeTranscriptApi, *_ = import_youtube_transcript_api()
    api = YouTubeTranscriptApi()
    items = []
    for transcript in api.list(parse_youtube_id(source)):
        items.append(
            {
                "language_code": transcript.language_code,
                "language": transcript.language,
                "kind": "auto" if transcript.is_generated else "manual",
                "source": "youtube-transcript-api",
                "is_translatable": transcript.is_translatable,
            }
        )
    return items


def fetch_youtube(source: str, languages: list[str]) -> tuple[list[dict], dict]:
    (
        YouTubeTranscriptApi,
        CouldNotRetrieveTranscript,
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    ) = import_youtube_transcript_api()
    try:
        fetched = YouTubeTranscriptApi().fetch(parse_youtube_id(source), languages=languages)
    except (CouldNotRetrieveTranscript, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as exc:
        raise TranscriptError(f"YouTube transcript unavailable: {exc}") from exc

    raw = fetched.to_raw_data() if hasattr(fetched, "to_raw_data") else list(fetched)
    segments = [
        {
            "start": float(item.get("start", 0)),
            "duration": float(item.get("duration", 0)),
            "text": clean_text(str(item.get("text", ""))),
        }
        for item in raw
        if clean_text(str(item.get("text", "")))
    ]
    meta = {
        "backend": "youtube-transcript-api",
        "language": getattr(fetched, "language", ""),
        "language_code": getattr(fetched, "language_code", ""),
        "generated": bool(getattr(fetched, "is_generated", False)),
        "source_url": f"https://www.youtube.com/watch?v={parse_youtube_id(source)}",
        "video_id": parse_youtube_id(source),
    }
    return segments, meta


def parse_srt(text: str) -> list[dict]:
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").replace("\r", "\n").strip())
    segments = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if re.fullmatch(r"\d+", lines[0]):
            lines = lines[1:]
        if not lines or "-->" not in lines[0]:
            continue
        start_text, _, end_text = lines[0].partition("-->")
        try:
            start = parse_stamp(start_text.strip())
            end = parse_stamp(end_text.strip().split()[0])
        except ValueError:
            continue
        body = clean_text(" ".join(lines[1:]))
        if body:
            segments.append({"start": start, "duration": max(0, end - start), "text": body})
    return segments


def parse_vtt(text: str) -> list[dict]:
    text = re.sub(r"^WEBVTT.*?(?:\n\s*\n)", "", text.replace("\r\n", "\n").replace("\r", "\n"), flags=re.S)
    blocks = re.split(r"\n\s*\n", text.strip())
    segments = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        cue = next((i for i, line in enumerate(lines) if "-->" in line), -1)
        if cue < 0:
            continue
        start_text, _, end_text = lines[cue].partition("-->")
        try:
            start = parse_stamp(start_text.strip())
            end = parse_stamp(end_text.strip().split()[0])
        except ValueError:
            continue
        body = clean_text(" ".join(lines[cue + 1 :]))
        if body:
            segments.append({"start": start, "duration": max(0, end - start), "text": body})
    return segments


def parse_plain_text(text: str) -> list[dict]:
    segments = []
    current_time: float | None = None
    current_lines: list[str] = []
    stamp_re = re.compile(r"^\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s*(.*)$")

    def flush() -> None:
        nonlocal current_lines, current_time
        body = clean_text(" ".join(current_lines))
        if body:
            segments.append({"start": current_time, "duration": 0, "text": body})
        current_lines = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            flush()
            current_time = None
            continue
        match = stamp_re.match(stripped)
        if match:
            flush()
            current_time = parse_stamp(match.group(1))
            if match.group(2).strip():
                current_lines.append(match.group(2).strip())
        else:
            current_lines.append(stripped)
    flush()

    if segments:
        return segments
    body = clean_text(text)
    return [{"start": None, "duration": 0, "text": body}] if body else []


def ingest_file(path: Path) -> tuple[list[dict], dict]:
    text = path.read_text(encoding="utf-8-sig")
    suffix = path.suffix.lower()
    if suffix == ".srt":
        segments = parse_srt(text)
    elif suffix == ".vtt":
        segments = parse_vtt(text)
    else:
        segments = parse_plain_text(text)
    if not segments:
        raise TranscriptError(f"No transcript segments parsed from {path}")
    return segments, {
        "backend": "local-file",
        "language": "",
        "language_code": "",
        "generated": False,
        "source_url": str(path),
        "video_id": "",
    }


def run_yt_dlp(args: list[str]) -> subprocess.CompletedProcess:
    candidates = [
        [sys.executable, "-m", "yt_dlp"],
        ["yt-dlp"],
    ]
    last: FileNotFoundError | None = None
    for base in candidates:
        try:
            result = subprocess.run(base + args, text=True, capture_output=True)
        except FileNotFoundError as exc:
            last = exc
            continue
        combined = (result.stderr or "") + (result.stdout or "")
        if result.returncode == 0:
            return result
        if "No module named yt_dlp" in combined:
            continue
        raise TranscriptError((result.stderr or result.stdout or "yt-dlp failed").strip())
    raise TranscriptError("Missing dependency for generic video sites: install with `python -m pip install yt-dlp`.") from last


def list_ytdlp(source: str) -> list[dict]:
    result = run_yt_dlp(["--skip-download", "--list-subs", source])
    return [{"raw": line} for line in result.stdout.splitlines() if line.strip()]


def fetch_ytdlp(source: str, languages: list[str]) -> tuple[list[dict], dict]:
    with tempfile.TemporaryDirectory() as temp:
        outtmpl = str(Path(temp) / "subtitle.%(ext)s")
        lang_arg = ",".join(languages) if languages else "all"
        run_yt_dlp(
            [
                "--skip-download",
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs",
                lang_arg,
                "--sub-format",
                "vtt/srt/best",
                "--output",
                outtmpl,
                source,
            ]
        )
        files = sorted(Path(temp).glob("subtitle.*"))
        subtitle_files = [file for file in files if file.suffix.lower() in {".vtt", ".srt"}]
        if not subtitle_files:
            raise TranscriptError("yt-dlp did not return subtitle files for this URL/language selection.")
        subtitle = subtitle_files[0]
        segments = parse_vtt(subtitle.read_text(encoding="utf-8-sig")) if subtitle.suffix.lower() == ".vtt" else parse_srt(subtitle.read_text(encoding="utf-8-sig"))
        if not segments:
            raise TranscriptError(f"No segments parsed from yt-dlp subtitle file: {subtitle.name}")
        return segments, {
            "backend": "yt-dlp",
            "language": "",
            "language_code": subtitle.stem.split(".")[-1] if "." in subtitle.stem else "",
            "generated": "auto" in subtitle.name.lower(),
            "source_url": source,
            "video_id": "",
        }


def infer_backend(source: str) -> str:
    if Path(source).exists():
        return "file"
    if is_youtube(source) or re.fullmatch(r"[A-Za-z0-9_-]{11}", source.strip()):
        return "youtube"
    if is_url(source):
        return "yt-dlp"
    raise TranscriptError(f"Source is neither an existing file nor a supported URL/video id: {source}")


def write_markdown(
    output: Path,
    *,
    source: str,
    title: str,
    speaker: str,
    channel: str,
    language_codes: list[str],
    meta: dict,
    segments: list[dict],
) -> None:
    source_url = meta.get("source_url") or source
    title_value = title or slug_title(Path(source).stem if Path(source).exists() else source_url)
    lines = [
        "---",
        f'title: "{title_value} transcript"',
        f'source: "{source_url}"',
        f'backend: "{meta.get("backend", "")}"',
        f'video_id: "{meta.get("video_id", "")}"',
        f'speaker: "{speaker}"',
        f'channel: "{channel}"',
        f'language: "{meta.get("language", "")}"',
        f'language_code: "{meta.get("language_code", "")}"',
        f'generated: {str(bool(meta.get("generated"))).lower()}',
        f'created: "{dt.date.today().isoformat()}"',
        "tags:",
        "  - transcript",
        "  - video-notes",
        "aliases:",
        f'  - "{title_value}"',
        "---",
        "",
        f"# {title_value}",
        "",
        "> [!note] Transcript source",
        f"> Created by `video_transcript_to_markdown.py` using `{meta.get('backend', '')}`. Auto-generated captions may need terminology cleanup.",
        "",
        "## Video Info",
        "",
        f"- Source: [{title_value}]({source_url})" if is_url(source_url) else f"- Source: `{source_url}`",
        f"- Speaker: {speaker}" if speaker else "- Speaker: ",
        f"- Channel: {channel}" if channel else "- Channel: ",
        f"- Requested languages: {', '.join(language_codes)}",
        f"- Transcript language: {meta.get('language', '')} ({meta.get('language_code', '')})",
        f"- Backend: {meta.get('backend', '')}",
        f"- Segments: {len(segments)}",
        "",
        "## Transcript",
        "",
    ]

    for item in segments:
        start = item.get("start")
        stamp = format_stamp(start)
        link = timestamp_link(source_url, start)
        heading = f"### [{stamp}]({link})" if link else f"### {stamp}"
        text = clean_text(str(item.get("text", "")))
        if text:
            lines.extend([heading, "", text, ""])

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch or ingest a video transcript and write timestamped Markdown for Obsidian."
    )
    parser.add_argument("source", help="YouTube URL/ID, other video URL, or local .srt/.vtt/.txt/.md transcript")
    parser.add_argument("--output", "-o", help="Output Markdown path. Required unless --list is used.")
    parser.add_argument("--title", default="", help="Optional video title")
    parser.add_argument("--speaker", default="", help="Optional speaker name")
    parser.add_argument("--channel", default="", help="Optional channel/source name")
    parser.add_argument("--languages", default="en,zh-Hans,zh-CN,zh", help="Comma-separated preferred language codes")
    parser.add_argument("--backend", choices=["auto", "youtube", "yt-dlp", "file"], default="auto")
    parser.add_argument("--list", action="store_true", help="List available subtitle/transcript tracks and exit")
    args = parser.parse_args()

    try:
        backend = infer_backend(args.source) if args.backend == "auto" else args.backend
        languages = [part.strip() for part in args.languages.split(",") if part.strip()]

        if args.list:
            if backend == "youtube":
                for item in list_youtube(args.source):
                    print(
                        f"{item['language_code']}\t{item['language']}\t{item['kind']}\t"
                        f"{'translatable' if item['is_translatable'] else 'not-translatable'}\t{item['source']}"
                    )
            elif backend == "yt-dlp":
                for item in list_ytdlp(args.source):
                    print(item["raw"])
            elif backend == "file":
                print("local-file\tUse --output to convert this transcript file to Markdown.")
            return 0

        if not args.output:
            raise TranscriptError("--output/-o is required unless --list is used.")

        if backend == "youtube":
            segments, meta = fetch_youtube(args.source, languages)
        elif backend == "yt-dlp":
            segments, meta = fetch_ytdlp(args.source, languages)
        elif backend == "file":
            segments, meta = ingest_file(Path(args.source))
        else:
            raise TranscriptError(f"Unsupported backend: {backend}")

        write_markdown(
            Path(args.output),
            source=args.source,
            title=args.title,
            speaker=args.speaker,
            channel=args.channel,
            language_codes=languages,
            meta=meta,
            segments=segments,
        )
        print(f"wrote={args.output}")
        print(f"backend={meta.get('backend')}")
        print(f"segments={len(segments)}")
        print(f"chars={sum(len(str(item.get('text', ''))) for item in segments)}")
        return 0
    except TranscriptError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
