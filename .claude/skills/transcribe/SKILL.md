---
name: transcribe
description: Typeset Carlos's final handwritten attempt into hw/hwN/hwN.tex verbatim and build the PDF. Usage - /transcribe hw4 [attemptK]
---
Transcription mode. Read `CLAUDE.md` hard rule 4 first. You are a typist, not a coauthor.
1. Read the photos in `hw/hwN/attempts/attemptK/` (latest K unless given). Create `hw/hwN/hwN.tex` from `templates/hw_template.tex` if it does not exist (or run `tools/new_hw.sh`).
2. Type exactly what is written: same claims, same steps, same order, same words. Convert math to proper LaTeX. Use the template's `\problem`, `\parta`, `claim`, `proof` environments for structure only.
3. Allowed edits: spelling, LaTeX syntax, math notation (e.g. `*` -> `\cdot`, `log` -> `\log`), paragraph breaks, numbering. NOT allowed: adding a missing case, completing an argument, fixing an inequality, deleting a wrong step, rewording a claim to make it true.
4. Anything illegible, ambiguous, or that you believe is a math error: transcribe your best reading and wrap a flag: `\todo{illegible: ...}` or `\todo{check: you wrote X, is that what you meant?}`. Do not say what the right thing is.
5. Fill the header: `\hwnumber`, `\duedate` (from the problem PDF), `\groupmembers` (ask if unknown).
6. Run `tools/build.sh hw/hwN/hwN.tex`. Fix only LaTeX errors. Report the list of `\todo` flags; Carlos resolves each by hand (new photo or verbal instruction that you then type verbatim).
7. Submission is his job. When he says it is submitted, write `submitted` to `hw/hwN/STATUS`.

## Logging (mandatory)
At the end of the session, if the work touched a homework, run `tools/log.sh N transcribe "<one-line process summary>"`. Process only: which mode, which attempt, counts of gaps named, anything refused. Never quote the problem, his claims, or any math. The log is published on nymo.finance.
