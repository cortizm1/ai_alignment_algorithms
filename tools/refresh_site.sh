#!/usr/bin/env bash
# Re-mirror homework/recitation/practice-exam files from the course site (new HWs appear every ~2 weeks).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; B=https://introalgorithmsfall26.cs.jhu.edu
cd "$root/course_site_raw"
for p in index schedule policies resources assignments; do
  curl -sfL -A Mozilla/5.0 "$B/$([ "$p" = index ] && echo index.html || echo "$p/")" -o "$p.html"; done
for i in $(seq 1 10); do for f in hw$i.pdf hw$i.tex; do
  curl -sfL -A Mozilla/5.0 "$B/assignments/Homeworks/$f" -o "Homeworks/$f" 2>/dev/null && echo "got $f" || rm -f "Homeworks/$f"; done; done
for i in $(seq 1 14); do curl -sfL -A Mozilla/5.0 "$B/schedule/Recitations/recitation$i.pdf" -o "Recitations/recitation$i.pdf" 2>/dev/null || rm -f "Recitations/recitation$i.pdf"; done
for f in midterm1 midterm1_solutions midterm2 midterm2_solutions final final_solutions; do
  curl -sfL -A Mozilla/5.0 "$B/assignments/PracticeExams/$f.pdf" -o "PracticeExams/$f.pdf" 2>/dev/null || rm -f "PracticeExams/$f.pdf"; done
for i in $(seq 1 25); do mkdir -p Lectures/Lecture$i; for v in lecture$i.pdf lecture${i}slides-Dinitz.pdf annotated-slides-Dinitz.pdf lecture${i}slides-Sorrell.pdf annotated-slides-Sorrell.pdf; do
  [ -f "Lectures/Lecture$i/$v" ] || curl -sfL -A Mozilla/5.0 "$B/schedule/Lectures/Lecture$i/$v" -o "Lectures/Lecture$i/$v" 2>/dev/null || rm -f "Lectures/Lecture$i/$v"; done; rmdir Lectures/Lecture$i 2>/dev/null || true; done
echo "mirror refreshed: $(ls Homeworks | tr '\n' ' ')"
