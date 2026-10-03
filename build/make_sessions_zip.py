"""Build a sessions-only archive small enough for the upload limit.

    python build/make_sessions_zip.py

Writes ../tasdemir_orcun_a1_sessions.zip containing, for all eight sessions,
the readable transcript rendering plus sessions/README.md and the renderer
that produced them.

Why not the raw .jsonl.  They are 72 MB uncompressed and 36 MB zipped, over
the upload limit; even LZMA only reaches 9 MB for the two full threads, and
an LZMA zip does not open reliably on every machine.  The export sheet offers
the raw file and the readable export as alternatives and says of the
equivalent Codex pair that the readable form "is what I ask for" and the raw
"is what saves you if the readable copy failed".  The .txt files here are
complete: render_transcript.py writes every message, every tool call with its
arguments and every tool result in full, with nothing truncated.  The raw
files remain in the project repository and are available on request.
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "tasdemir_orcun_a1_sessions"
OUT = ROOT.parent / f"{NAME}.zip"
SESS = ROOT / "sessions"

members = [(SESS / "README.md", f"{NAME}/sessions/README.md"),
           (SESS / "render_transcript.py", f"{NAME}/sessions/render_transcript.py")]
for p in sorted((SESS / "claude-code").glob("*.txt")):
    members.append((p, f"{NAME}/sessions/claude-code/{p.name}"))

for src, _ in members:
    if not src.exists():
        raise SystemExit(f"missing: {src}")

OUT.unlink(missing_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for src, arc in members:
        z.write(src, arc)

print(f"wrote {OUT}")
print(f"  {len(members)} files, {OUT.stat().st_size / 1e6:.1f} MB")
