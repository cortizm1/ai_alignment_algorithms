---
name: postmortem
description: After a homework is graded, compare Carlos's writeup with the released solutions and extract lessons (green zone). Usage - /postmortem hw3
---
1. Require `hw/hwN/STATUS` = `graded`. If not, stop: "set STATUS to graded once grades and official solutions are out."
2. Inputs: his submission (`hw/hwN/hwN.tex` or attempt photos), the official solutions (he downloads them from Canvas into `hw/hwN/solutions.pdf`; never fetch them yourself), Gradescope rubric comments if he pastes them.
3. For each part: what the official solution's structure is, where his diverged, and classify each lost point as one of: (a) wrong claim, (b) right claim wrong technique, (c) right technique missing rigor, (d) right proof badly communicated, (e) typesetting/format.
4. Produce `hw/hwN/postmortem.md` with the classification table and 3 concrete drills (CLRS exercise numbers or recitation problems) targeting the biggest category.
5. Append the lessons to `study/lessons.md` (running list across homeworks).
Full discussion of the solutions is allowed here; they are instructor-released.

## Logging (mandatory)
At the end of the session, if the work touched a homework, run `tools/log.sh N postmortem "<one-line process summary>"`. Process only: which mode, which attempt, counts of gaps named, anything refused. Never quote the problem, his claims, or any math. The log is published on nymo.finance.
