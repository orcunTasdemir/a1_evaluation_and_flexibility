"""Build the submission archive.

    python build/make_submission.py

Writes ../tasdemir_orcun_a1.zip in the layout
course_docs/04_submission_checklist.md specifies:

    tasdemir_orcun_a1/
      memo.pdf, memo.md
      ai_process_note.md, ai_process_note.pdf
      analysis/   run.sh, README.md, the code, outputs/
      sessions/   README.md, render_transcript.py, and the readable .txt
                  transcript of all eight sessions (the raw .jsonl are too
                  large for the upload limit; see sessions/README.md)

Deliberately excluded, per that checklist: the two data folders (the graders
have them), the virtual environment, and any __pycache__.  Also excluded
because they are not part of the submission: the supplied starter code,
course_docs/, handouts/, drafts/, build/, NOTES.md, CLAUDE.md,
questions.txt, requirements.txt and the brief itself.

analysis/ reads the data in place from ../part1_northline/data and
../part2_cascade/data, so this unpacks alongside the grader's own copy of
the assignment folder.

Written with zipfile rather than PowerShell's Compress-Archive, which stores
entry names with backslashes; those unpack as flat files with literal
backslashes in the name on macOS and Linux.
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "tasdemir_orcun_a1"
OUT = ROOT.parent / f"{NAME}.zip"

FILES = ["memo.pdf", "memo.md", "ai_process_note.md", "ai_process_note.pdf"]
TREES = ["analysis", "sessions"]
SKIP_DIRS = {"__pycache__", ".venv", ".git"}
SKIP_SUFFIX = {".pyc", ".pyo"}

# Transcripts: the readable .txt rendering of all eight sessions goes in, and
# the raw .jsonl does not.  The raw files are 72 MB uncompressed and 36 MB
# zipped, over the upload limit; even LZMA reaches only 9 MB for the two
# largest, and an LZMA archive does not open reliably everywhere.  The .txt
# renderings are complete: render_transcript.py writes every message, every
# tool call with its arguments and every tool result in full, nothing
# truncated.  The export sheet offers the raw file and the readable export as
# alternatives and treats the readable form as the one it asks for.  The raw
# files stay in the repository and sessions/README.md says they are available
# on request.


def is_redundant_transcript(path: Path) -> bool:
    """True for the raw transcripts, which are left out for size."""
    return path.parent.name == "claude-code" and path.suffix == ".jsonl"


def members():
    for f in FILES:
        p = ROOT / f
        if not p.exists():
            raise SystemExit(f"missing deliverable: {f}")
        yield p, f"{NAME}/{f}"
    for tree in TREES:
        base = ROOT / tree
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if p.suffix in SKIP_SUFFIX:
                continue
            if is_redundant_transcript(p):
                continue
            yield p, f"{NAME}/{p.relative_to(ROOT).as_posix()}"


OUT.unlink(missing_ok=True)
n = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for src, arc in members():
        z.write(src, arc)
        n += 1

size = OUT.stat().st_size / 1e6
print(f"wrote {OUT}")
print(f"  {n} files, {size:.1f} MB")
