#!/usr/bin/env bash
# Scaffold hw/hwN from the course mirror and the template.
# Usage: tools/new_hw.sh 5 "October 22, 2026"
set -euo pipefail
n="${1:?usage: tools/new_hw.sh N [due date]}"; due="${2:-Month DD, 2026}"
root="$(cd "$(dirname "$0")/.." && pwd)"
d="$root/hw/hw$n"
mkdir -p "$d/attempts/attempt1" "$d/feedback"
src="$root/course_site_raw/Homeworks"
[ -f "$src/hw$n.pdf" ] && cp "$src/hw$n.pdf" "$d/" || echo "note: $src/hw$n.pdf not mirrored yet; refetch with tools/refresh_site.sh"
[ -f "$src/hw$n.tex" ] && cp "$src/hw$n.tex" "$d/problem.tex" || true
sed -e "s/\\\\newcommand{\\\\hwnumber}{N}/\\\\newcommand{\\\\hwnumber}{$n}/" \
    -e "s/\\\\newcommand{\\\\duedate}{Month DD, 2026}/\\\\newcommand{\\\\duedate}{$due}/" \
    "$root/templates/hw_template.tex" > "$d/hw$n.tex"
echo live > "$d/STATUS"
echo "created $d  (STATUS=live). Put photos in attempts/attempt1/, then /critique hw$n"
