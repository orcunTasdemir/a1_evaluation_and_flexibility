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

## Size note

Session 2's transcript is about 10 MB because the agent read the course
handout PDFs page by page and the page images are embedded in the record.
That is course material, not private data.

## Sessions

| # | Date | Machine | Topic |
|---|---|---|---|
| 1 | 2026-09-17 | Windows 11 | Setup only. Folder audit, Python environment, `.gitignore` fix, `NOTES.md`. No analysis. |
| 2 | 2026-09-17 | macOS | Mac environment, handouts added, concept review (Handouts 1, 2, R1), A1 baselines script and draft. |
| 3 | 2026-09-20 | Windows 11 | A1 review quiz and finalisation, `prep.py` refactor, A2 evaluation built and drafted. |

Sessions 1 and 3 are the same VS Code conversation, continued on a later
day. `a1-session-3.jsonl` is therefore the full thread and contains session 1
as its first part; `a1-session-1.jsonl` is the earlier snapshot of the same
thread. Neither is sliced or edited.
