# AI sessions for Assignment 1

Agent used: Claude Code (VS Code extension, on a Windows 11 desktop and a macOS laptop)

- `claude-code/` : one `.jsonl` and one `.txt` per session.

## How these were exported, and why not with `/export`

`03_exporting_your_session_history.md` gives two options for Claude Code:
Option A, the raw JSONL at `~/.claude/projects/<encoded-path>/<session-id>.jsonl`,
and Option B, `/export` from inside a session.

**Option B is not available in the VS Code extension.** Running
`/export sessions/claude-code/a1-session-1.txt` there returns "/export isn't
available in this environment". The `claude` CLI has no `export` subcommand
either (checked against `claude --help` on 2026-09-17, CLI version 2.52-era
build). So, per the sheet's closing instruction to find the equivalent and say
what was done instead:

1. **Option A, unchanged.** The raw transcript is copied verbatim to
   `claude-code/a1-session-N.jsonl`. This is the complete record.
2. **Option B, reproduced.** `render_transcript.py` in this folder renders that
   JSONL as readable text at `claude-code/a1-session-N.txt`. It writes out every
   user and assistant message, every tool call with its arguments, and every
   tool result in full, with nothing truncated. Run it with:

       python sessions/render_transcript.py \
           sessions/claude-code/a1-session-1.jsonl \
           sessions/claude-code/a1-session-1.txt

Both files are submitted. The JSONL is authoritative; the `.txt` is for reading.

## Known gap

Each transcript is copied from disk near the end of its session, so it stops a
few messages short of the true end. The missing tail is the export and the
`git commit`/`git push` that followed it, which are visible in the repository
history. Nothing about the analysis is lost this way.

## Images in the readable rendering

The agent read the course handout PDFs page by page, so the raw transcripts
embed those pages as base64 images. In `a1-session-4.jsonl` they were 93% of
the rendered text, which made the readable `.txt` unreadable -- the opposite
of what it is for.

`render_transcript.py` therefore writes an image as a labelled placeholder
giving its media type and payload size, for example:

    [image omitted from the readable rendering: image/png, 412,336 base64
     chars; the full payload is in the .jsonl]

**Nothing is removed from the record.** The `.jsonl` files are byte-for-byte
as Claude Code wrote them, images included, and they are the authoritative
submission; only the derived readable view substitutes the placeholder. The
images are course handout pages, not private data. `sessions/` is about 62 MB,
most of it the `.jsonl` files.

## Size

`sessions/` is about 62 MB, nearly all of it the `.jsonl` transcripts, which
embed the course handout pages the agent read. The export sheet says to zip the
folder and say so if it exceeds roughly 50 MB; if the submission archive is
unwieldy, `sessions/claude-code/` is the part to compress. The `.txt` renderings
are small — the images in them are replaced by a labelled placeholder, as
described above.

## Sessions

| # | Date | Machine | Topic |
|---|---|---|---|
| 1 | 2026-09-17 | Windows 11 | Setup only. Folder audit, Python environment, `.gitignore` fix, `NOTES.md`. No analysis. |
| 2 | 2026-09-17 | macOS | Mac environment, handouts added, concept review (Handouts 1, 2, R1), A1 baselines script and draft. |
| 3 | 2026-09-20 | Windows 11 | A1 review quiz and finalisation, `prep.py` refactor, A2 evaluation built and drafted. |
| 4 | 2026-09-29 | macOS | A3: cost-based threshold, calibration on the validation month, realised value on the test quarter, draft. Part A complete. |
| 5 | 2026-09-29 | macOS | B1: the noise floor, with the estimator's assumption verified. Handout 3 read. A2 data-selection caveats recorded. |
| 6 | 2026-10-01 | Windows 11 | B2: four models against the floor, contractor's figures reproduced. B3: the stability experiment, supplied loop run as issued. Part B complete. |
| 7 | 2026-10-01 | macOS | memo.md and ai_process_note.md drafted; memo-number checker added. |
| 8 | 2026-10-02 | Windows 11 | Part A of the memo edited and vetted; per-segment standard errors added; figures embedded. |

There are two VS Code conversations, worked in repeatedly, so four of the
six files contain an earlier file as their opening part. Nothing is sliced,
truncated or edited; the last file in each chain is the full thread and the
earlier ones are snapshots taken at the end of each sitting.

| File | Records | Relationship |
|---|---:|---|
| `a1-session-1.jsonl` | 245 | thread A, snapshot after session 1 |
| `a1-session-3.jsonl` | 636 | thread A after session 3; its first 245 records are byte-identical to `a1-session-1.jsonl` |
| `a1-session-6.jsonl` | 1,184 | thread A after session 6; its first 636 records are byte-identical to `a1-session-3.jsonl` |
| `a1-session-8.jsonl` | 2,343 | thread A in full; its first 1,184 records are byte-identical to `a1-session-6.jsonl` |
| `a1-session-2.jsonl` | 637 | thread B, snapshot after session 2 |
| `a1-session-4.jsonl` | 1,134 | thread B after session 4; its first 637 records are byte-identical to `a1-session-2.jsonl` |
| `a1-session-5.jsonl` | 1,339 | thread B after session 5; its first 1,134 records are byte-identical to `a1-session-4.jsonl` |
| `a1-session-7.jsonl` | 1,762 | thread B in full; its first 1,339 records are byte-identical to `a1-session-5.jsonl` |

Both containments were verified with `cmp`, not asserted. All eight files are
submitted rather than only the two full threads, because the snapshots are
what existed at the end of each working session and removing them would be
curating the record.
