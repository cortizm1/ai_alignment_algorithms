#!/usr/bin/env bash
# Append an AI-usage entry to a homework's public log. Process metadata only, never content.
# Usage: tools/log.sh 4 critique "attempt1 reviewed; 3 rigor gaps named in P1a, P2b; no hints given"
set -euo pipefail
n="${1:?hw number}"; mode="${2:?mode}"; note="${3:?note}"
f="$(cd "$(dirname "$0")/.." && pwd)/hw/hw$n/ai_log.md"
[ -f "$f" ] || printf '# HW%s AI-usage log\n\n| when (local) | mode | what happened |\n|---|---|---|\n' "$n" > "$f"
printf '| %s | %s | %s |\n' "$(date '+%Y-%m-%d %H:%M')" "$mode" "$note" >> "$f"
echo "logged -> $f"
