---
name: exam-prep
description: Timed practice exam sessions and proof drills from released material (green zone). Usage - /exam-prep midterm2 | /exam-prep proofs
---
1. Material: `course_site_raw/PracticeExams/`, graded homeworks, recitations, lecture notes, CLRS exercises, the Hutchings proof handout (`course_site_raw/hutchings.pdf`).
2. `/exam-prep proofs`: run the proof-writing curriculum in `docs/study_plan.md` §Proof curriculum. One technique per session: direct, contrapositive, contradiction, induction (weak/strong), exchange argument, potential function, probabilistic (expectation, union bound). For each: he proves a small known lemma by hand, photographs it, you grade it with the /critique rubric but in FULL mode (you may show the model proof afterwards, since nothing here is live homework).
3. `/exam-prep midterm2` or `final`: assemble a timed set (75 min for midterm, 180 for final) from the allowed material covering the topics in `course_site_raw/SCRAPE_NOTES.md`. He works on paper with no tools; then photographs; you grade against a rubric and give model answers.
4. Log results in `study/exam_prep/<date>.md` with a per-topic score so weak topics surface.

## Logging (mandatory)
At the end of the session, if the work touched a homework, run `tools/log.sh N exam-prep "<one-line process summary>"`. Process only: which mode, which attempt, counts of gaps named, anything refused. Never quote the problem, his claims, or any math. The log is published on nymo.finance.
