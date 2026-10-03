#!/usr/bin/env bash
# Render the two prose deliverables to PDF.
#
#     bash build/make_pdfs.sh
#
# Not part of analysis/run.sh: that command exists to reproduce the numbers
# on a clean clone, and it must not depend on a LaTeX installation.  This
# needs pandoc and a LaTeX engine (xelatex), which the grader is not assumed
# to have; memo.md and ai_process_note.md are readable without it.
#
# Font sizes are chosen so each document meets its stated limit:
#
#   memo.pdf              10pt, 1in margins   -> S1 prose 2 pages, S2 prose 1
#   ai_process_note.pdf   10pt, 0.8in margins -> 1 page
#
# Horizontal rules in memo.md become page breaks (build/pagebreak.lua), so
# the prose sections occupy whole pages and the limits can be checked by
# looking at the page numbers.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

COMMON=(--pdf-engine=xelatex -V mainfont=Calibri -V monofont=Consolas
        -V fontsize=10pt -V colorlinks=true -V linkcolor=black)

pandoc "$ROOT/memo.md" -o "$ROOT/memo.pdf" \
  "${COMMON[@]}" -V geometry:margin=1in --lua-filter="$HERE/pagebreak.lua"

pandoc "$ROOT/ai_process_note.md" -o "$ROOT/ai_process_note.pdf" \
  "${COMMON[@]}" -V geometry:margin=0.8in

echo "wrote memo.pdf and ai_process_note.pdf"
