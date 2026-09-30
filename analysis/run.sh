#!/usr/bin/env bash
# One command for the whole analysis.  Run from anywhere:
#
#     bash analysis/run.sh
#
# Everything lands in analysis/outputs/.  Stdout is also saved there as
# run.log so every number in the memo has a printed source.
set -euo pipefail

# Importing the supplied starter modules would otherwise drop __pycache__
# folders into part1_northline/ and part2_cascade/.  Leave those folders as
# they were issued.
export PYTHONDONTWRITEBYTECODE=1

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
OUT="$HERE/outputs"
mkdir -p "$OUT"

# Use the project .venv if it exists, otherwise whatever python3 is on PATH.
if [ -x "$ROOT/.venv/bin/python" ]; then PY="$ROOT/.venv/bin/python"
elif [ -x "$ROOT/.venv/Scripts/python.exe" ]; then PY="$ROOT/.venv/Scripts/python.exe"
else PY="python3"; fi

{
  echo "=== environment ==="
  "$PY" --version
  "$PY" -c "import numpy, pandas, sklearn, matplotlib; print('numpy', numpy.__version__, '| pandas', pandas.__version__, '| sklearn', sklearn.__version__, '| matplotlib', matplotlib.__version__)"
  echo

  # The analyst's pipeline, run exactly as supplied, from its own folder.  It
  # prints the headline the brief quotes; its output is kept so A1 can put
  # that number beside the baselines without anyone retyping it.
  echo "=== part1: analyst_model.py (as supplied) ==="
  "$PY" "$ROOT/part1_northline/starter/analyst_model.py" | tee "$OUT/analyst_model_output.txt"
  echo

  echo "=== part1: A1 baselines ==="
  "$PY" "$HERE/part1/a1_baselines.py"
  echo

  echo "=== part1: A2 evaluation ==="
  "$PY" "$HERE/part1/a2_evaluation.py"
  echo

  echo "=== part1: A3 targeting decision ==="
  "$PY" "$HERE/part1/a3_decision.py"
  echo
} 2>&1 | tee "$OUT/run.log"
