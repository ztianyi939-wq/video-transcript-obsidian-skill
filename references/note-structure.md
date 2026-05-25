# Obsidian Video Note Structure

Use this reference when turning a raw transcript into a readable Obsidian note.

## Default Frontmatter

```yaml
---
title: "<video title> 精读笔记"
source: "<video url or transcript path>"
speaker: "<speaker if known>"
channel: "<channel/source if known>"
created: "YYYY-MM-DD"
tags:
  - video-notes
  - tech-talk
aliases:
  - "<short title>"
---
```

Add domain tags from the transcript, such as `CMOS`, `image-sensor`, `ADC`, `semiconductor`, `machine-learning`, `systems`, `biology`, `finance`, or `history`.

## Default Sections

```markdown
# <Video Title> 精读笔记

> [!note] 来源说明
> 本笔记根据视频 transcript 整理；若字幕为自动生成，已尽量校正明显术语误识别。

## 一句话总结

## 核心脉络

## 时间线笔记

| 时间 | 主题 | 笔记 |
|---|---|---|
| [00:00](<timestamp link>) | 开场 | ... |

## 关键概念整理

## 演讲中特别值得记的观点

## 术语表

## 复习问题

## 相关笔记

## 原始视频
```

## Language Handling

- Preserve the raw transcript language in the transcript file.
- If transcript language is English and the user wants Chinese notes, summarize and explain in Chinese; keep key English technical terms in parentheses on first mention.
- If transcript language is Chinese, keep Chinese as the main note language and preserve important English acronyms.
- If multiple caption tracks exist, prefer the user-requested language; otherwise prefer manual captions, then English, then Chinese auto captions.
- If the transcript mixes languages, do not force full translation in the raw transcript. Normalize only the cleaned note.

## Topic-General Synthesis

- Infer the domain from repeated terms, title, channel, and section flow.
- Create domain-specific tags and a terminology table.
- For technical talks, emphasize architecture, mechanisms, tradeoffs, formulas, examples, and failure modes.
- For humanities/business talks, emphasize thesis, argument structure, evidence, cases, implications, and open questions.
- Do not use the CMOS terminology table blindly for unrelated topics; use it only when relevant.

## Transcript Cleanup

- Merge tiny caption fragments into paragraphs before reasoning.
- Keep timestamp links at topic boundaries, not every sentence.
- Prefer conceptual headings over minute-by-minute headings.
- Mark uncertainty when ASR text is unclear.
- Do not quote long transcript passages; summarize and paraphrase.

## Common Technical ASR Corrections

| Wrong/likely ASR text | Correct term |
|---|---|
| seos, cimos, semos | CMOS |
| ad see, a to d | ADC / A-to-D converter |
| columbus, column buses | column bus / column buses |
| ram generator | ramp generator |
| ram cell | ramp cell or memory cell, depending on context |
| ro select, rose elect | row select |
| source follow | source follower |
| photo diet | photodiode |
| transfer Gates | transfer gates |
| ktc | kTC noise |
| one over F | 1/f noise |
| correlated double sampling | correlated double sampling (CDS) |
| image signal process | image signal processor (ISP) |
| demos sensing | demosaicing |

## Quality Checklist

- Frontmatter has exactly one opening and one closing `---` block.
- External video links use normal Markdown links.
- Vault-internal references use wikilinks.
- At least five meaningful timestamp links remain in long talks when timestamps are available.
- The cleaned note is readable without opening the raw transcript.
- The raw transcript note is linked from the cleaned note.
- No mojibake, replacement characters, or mixed encoding artifacts appear in Chinese text.
