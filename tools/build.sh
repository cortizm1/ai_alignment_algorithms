#!/usr/bin/env bash
# Compile a homework .tex into a PDF next to it. Runs pdflatex twice for references.
# Usage: tools/build.sh hw/hw4/hw4.tex
set -euo pipefail
tex="${1:?usage: tools/build.sh path/to/file.tex}"
dir="$(dirname "$tex")"; base="$(basename "$tex" .tex)"
cd "$dir"
for i in 1 2; do
  pdflatex -interaction=nonstopmode -halt-on-error "$base.tex" > "$base.build.log" 2>&1 || {
    echo "BUILD FAILED. First errors:"; grep -nE '^!|^l\.[0-9]+' "$base.build.log" | head -20; exit 1; }
done
rm -f "$base.aux" "$base.out" "$base.log" "$base.build.log"
if grep -q 'TODO:' "$base.tex"; then
  echo "WARNING: $base.tex still has \\todo{} markers:"; grep -n 'todo{' "$base.tex" | grep -v '^.*%' | head
fi
echo "OK -> $dir/$base.pdf ($(mutool info "$base.pdf" 2>/dev/null | grep -i '^Pages' || echo 'pages: ?'))"
