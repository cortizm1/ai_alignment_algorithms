# 601.433 Intro to Algorithms — study harness

Paper first. Claude is an office-hours CA and a typist, never a solver. Rules in `CLAUDE.md`.

## Homework loop
1. `tools/new_hw.sh N "Month DD, 2026"` -> `hw/hwN/` with the problem and a template.
2. Attempt on paper. Photos -> `hw/hwN/attempts/attempt1/`.
3. `/critique hwN` -> `hw/hwN/feedback/attempt1.md` (gaps named, not filled). Discuss concepts.
4. Attempt again on paper -> `attempts/attempt2/`. Repeat 3 if needed.
5. `/transcribe hwN` -> `hw/hwN/hwN.tex` + PDF, verbatim. Resolve every red TODO by hand.
6. Submit on Gradescope. `echo submitted > hw/hwN/STATUS`.
7. When graded and solutions released: `echo graded > hw/hwN/STATUS`, download solutions to `hw/hwN/solutions.pdf`, `/postmortem hwN`.

## Study
`/concept`, `/quiz`, `/exam-prep` — see `docs/study_plan.md`.

## Setup still pending
`sudo apt install texlive-science latexmk poppler-utils` (pseudocode packages, auto-rebuild, pdftotext).
Everything else already compiles: `tools/build.sh hw/hw4/hw4.tex`.
